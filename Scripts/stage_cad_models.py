#!/usr/bin/env python3
"""Stage the CAD bake-off's 3D exports into the built app bundle.

Run as a build phase. Copies every renderable mesh under cad/ into
<bundle>/CADModels/<engine>/ and writes a manifest the app reads at launch.
STEP files are catalogued but not copied: nothing on iOS or macOS can tessellate
a B-rep, so only their ISO-10303-21 header is carried over (a few hundred bytes
instead of several megabytes).

The exports are kept out of the source tree on purpose — they live in cad/ as
build outputs of the bake-off, and staging them here means a rebuilt gripper
ships without anyone copying files around.
"""
import json
import os
import shutil
import sys

# (display name, directory under the repo root). Order is cosmetic; the app
# sorts engines by name.
SOURCES = [
    ("OpenSCAD", "cad/openscad/export"),
    ("Blender", "cad/blender/out"),
    ("build123d", "cad/build123d/export"),
    ("SO-101 reference", "cad/build123d/reference"),
]

RENDERABLE = {"stl", "obj", "ply", "usd", "usda", "usdc", "usdz", "abc"}
DESCRIBABLE = {"step", "stp"}


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
    return name.lower().replace(" ", "-")


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
    for engine, relative in SOURCES:
        directory = os.path.join(root, relative)
        if not os.path.isdir(directory):
            continue
        for entry in sorted(os.listdir(directory)):
            source = os.path.join(directory, entry)
            if not os.path.isfile(source) or entry.startswith("."):
                continue
            stem, dot, ext = entry.rpartition(".")
            ext = ext.lower()
            if not dot or (ext not in RENDERABLE and ext not in DESCRIBABLE):
                continue

            model = {
                "id": "%s/%s" % (slug(engine), entry),
                "name": stem,
                "engine": engine,
                "ext": ext,
                "bytes": os.path.getsize(source),
            }
            if ext in RENDERABLE:
                target_dir = os.path.join(dest, slug(engine))
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(source, os.path.join(target_dir, entry))
                model["path"] = "%s/%s" % (slug(engine), entry)
            else:
                header = step_header(source)
                if header:
                    model["header"] = header
            models.append(model)

    with open(os.path.join(dest, "manifest.json"), "w") as handle:
        json.dump({"models": models}, handle, indent=1)
    print("stage_cad_models: staged %d model(s) into %s" % (len(models), dest))


if __name__ == "__main__":
    main()
