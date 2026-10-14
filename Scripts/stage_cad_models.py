#!/usr/bin/env python3
"""Stage every CAD design under cad/ into the built app bundle.

Run as a build phase. A "design" is any folder under cad/ holding 3D exports —
either directly, or in an export/ or out/ subfolder — plus the PNG renders next
to them (render/, or loose in the export folder). Nothing is registered by
hand: an agent that drops a new design into cad/ makes it the app's first
screen on the next build, because designs are ordered newest-first by the last
commit that touched their exports or renders.

Every renderable mesh is copied into <bundle>/CADModels/<design>/, renders into
<bundle>/CADModels/<design>/images/, and a manifest the app reads at launch is
written alongside. STEP files are catalogued but not copied: nothing on iOS or
macOS can tessellate a B-rep, so only their ISO-10303-21 header is carried over
(a few hundred bytes instead of several megabytes).
"""
import json
import os
import shutil
import subprocess
import sys

# A folder with these names holds a design's exports; the design is its parent.
EXPORT_DIRS = {"export", "out"}
SKIP_DIRS = {"__pycache__", "node_modules", "render", "tools"}

RENDERABLE = {"stl", "obj", "ply", "usd", "usda", "usdc", "usdz", "abc"}
DESCRIBABLE = {"step", "stp"}
IMAGES = {"png", "jpg", "jpeg"}


def repo_root():
    root = os.environ.get("SRCROOT") or os.getcwd()
    while not os.path.isdir(os.path.join(root, ".git")) and root != "/":
        root = os.path.dirname(root)
    return root if root != "/" else (os.environ.get("SRCROOT") or os.getcwd())


def destination():
    if len(sys.argv) > 1:
        return sys.argv[1]
    products = os.environ.get("BUILT_PRODUCTS_DIR")
    resources = os.environ.get("UNLOCALIZED_RESOURCES_FOLDER_PATH")
    if not products or not resources:
        sys.stderr.write("stage_cad_models: no BUILT_PRODUCTS_DIR — pass a destination\n")
        sys.exit(2)
    return os.path.join(products, resources, "CADModels")


def slug(name):
    return name.lower().replace(" ", "-").replace("/", "-")


def extension(entry):
    stem, dot, ext = entry.rpartition(".")
    return (stem, ext.lower()) if dot else (entry, "")


def files_in(directory, kinds):
    if not os.path.isdir(directory):
        return []
    return [entry for entry in sorted(os.listdir(directory))
            if not entry.startswith(".")
            and os.path.isfile(os.path.join(directory, entry))
            and extension(entry)[1] in kinds]


def find_designs(cad):
    """Map each design folder to the folders its exports live in."""
    designs = {}
    for directory, subdirs, _ in os.walk(cad):
        subdirs[:] = sorted(d for d in subdirs
                            if not d.startswith(".") and d not in SKIP_DIRS)
        if not files_in(directory, RENDERABLE | DESCRIBABLE):
            continue
        design = directory
        if os.path.basename(directory) in EXPORT_DIRS:
            design = os.path.dirname(directory)
        designs.setdefault(design, []).append(directory)
    return designs


def title(design, root):
    """The design's README (or NOTES) heading, else its path under cad/."""
    for doc in ("README.md", "NOTES.md"):
        try:
            with open(os.path.join(design, doc), encoding="utf-8") as handle:
                for line in handle:
                    if line.startswith("# "):
                        return line[2:].strip(), doc
        except OSError:
            continue
    return os.path.relpath(design, os.path.join(root, "cad")).replace("/", " "), None


def updated_at(root, paths):
    """Unix time of the last commit touching any of `paths`; files that were
    never committed (a design dropped but not pushed yet) count by mtime."""
    newest = 0
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", "-1", "--format=%ct", "--"] + paths,
            capture_output=True, text=True, timeout=20).stdout.strip()
        newest = int(out) if out else 0
    except (OSError, ValueError, subprocess.SubprocessError):
        pass
    if newest == 0:
        for path in paths:
            for entry in os.listdir(path):
                newest = max(newest, int(os.path.getmtime(os.path.join(path, entry))))
    return newest


def primary(meshes):
    """The file to open first: a closed assembly if there is one, else the
    biggest mesh (the whole part beats a single pad)."""
    def rank(item):
        name = item["name"].lower()
        return ("assembly" in name and "open" not in name, item["bytes"])
    return max(meshes, key=rank)["id"] if meshes else None


def step_header(path):
    """Pull the readable fields out of a STEP file's HEADER section."""
    try:
        with open(path, "rb") as handle:
            text = handle.read(4096).decode("utf-8", "replace")
    except OSError:
        return {}
    head = text.split("ENDSEC")[0].replace("\n", " ").replace("\r", " ")

    def entity(name):
        start = head.find(name + "(")
        if start < 0:
            return ""
        end = head.find(");", start)
        return head[start + len(name) + 1:end if end > 0 else len(head)]

    def strings(chunk):
        parts = chunk.split("'")
        return [p.strip() for p in parts[1::2]]

    fields = {}
    name_parts = strings(entity("FILE_NAME"))
    if len(name_parts) > 0 and name_parts[0]:
        fields["Name"] = name_parts[0]
    if len(name_parts) > 1 and name_parts[1]:
        fields["Written"] = name_parts[1]
    if len(name_parts) > 5 and name_parts[5]:
        fields["Preprocessor"] = name_parts[5]
    if len(name_parts) > 6 and name_parts[6] and name_parts[6] != "Unknown":
        fields["Originating system"] = name_parts[6]
    desc = strings(entity("FILE_DESCRIPTION"))
    if desc and desc[0]:
        fields["Description"] = desc[0]
    schema = strings(entity("FILE_SCHEMA"))
    if schema and schema[0]:
        fields["Schema"] = schema[0]
    return fields


def main():
    root = repo_root()
    dest = destination()
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest, exist_ok=True)

    models = []
    designs = []
    for design_dir, export_dirs in sorted(find_designs(os.path.join(root, "cad")).items()):
        name, doc = title(design_dir, root)
        key = slug(os.path.relpath(design_dir, os.path.join(root, "cad")))
        target_dir = os.path.join(dest, key)

        design_models = []
        for directory in export_dirs:
            for entry in files_in(directory, RENDERABLE | DESCRIBABLE):
                source = os.path.join(directory, entry)
                stem, ext = extension(entry)
                model = {
                    "id": "%s/%s" % (key, entry),
                    "name": stem,
                    "engine": name,
                    "ext": ext,
                    "bytes": os.path.getsize(source),
                }
                if ext in RENDERABLE:
                    os.makedirs(target_dir, exist_ok=True)
                    shutil.copy2(source, os.path.join(target_dir, entry))
                    model["path"] = "%s/%s" % (key, entry)
                else:
                    header = step_header(source)
                    if header:
                        model["header"] = header
                design_models.append(model)

        image_dirs = [d for d in [os.path.join(design_dir, "render")] + export_dirs
                      if os.path.isdir(d)]
        images = []
        for directory in image_dirs:
            for entry in files_in(directory, IMAGES):
                os.makedirs(os.path.join(target_dir, "images"), exist_ok=True)
                shutil.copy2(os.path.join(directory, entry),
                             os.path.join(target_dir, "images", entry))
                images.append("%s/images/%s" % (key, entry))

        renderable = [m for m in design_models if "path" in m]
        designs.append({
            "id": key,
            "name": name,
            "folder": os.path.relpath(design_dir, root),
            "doc": doc,
            "updated": updated_at(root, image_dirs),
            "primary": primary(renderable) or (design_models[0]["id"] if design_models else None),
            "models": [m["id"] for m in design_models],
            "images": images,
        })
        models.extend(design_models)

    designs.sort(key=lambda d: d["updated"], reverse=True)
    with open(os.path.join(dest, "manifest.json"), "w") as handle:
        json.dump({"designs": designs, "models": models}, handle, indent=1)
    print("stage_cad_models: staged %d design(s), %d model(s) into %s"
          % (len(designs), len(models), dest))


if __name__ == "__main__":
    main()
