#!/usr/bin/env python3
"""Stage the repo's written plans into the built app bundle.

Run as a build phase. Copies every markdown plan under plans/ into
<bundle>/Plans/ and writes a manifest the app reads at launch, so a plan added
to the repo is listenable in the app on the next build without anyone touching
Swift or the Xcode project.
"""
import json
import os
import shutil
import sys

SOURCE_DIR = "plans"
EXTENSIONS = {"md", "markdown", "txt"}


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
        sys.stderr.write("stage_plans: no BUILT_PRODUCTS_DIR — pass a destination\n")
        sys.exit(2)
    return os.path.join(products, resources, "Plans")


def title_of(path, fallback):
    """The first level-one heading, which is how every plan in plans/ starts."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped.startswith("# "):
                    return stripped[2:].strip()
                if stripped.startswith("#"):
                    continue
    except OSError:
        pass
    pretty = fallback.replace("_", " ").replace("-", " ").strip()
    # Only title-case an all-lowercase stem, so "iBackpack" keeps its shape.
    return pretty.title() if pretty.islower() else pretty


def main():
    root = repo_root()
    source = os.path.join(root, SOURCE_DIR)
    dest = destination()
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest, exist_ok=True)

    plans = []
    if os.path.isdir(source):
        for entry in sorted(os.listdir(source)):
            path = os.path.join(source, entry)
            stem, dot, ext = entry.rpartition(".")
            if not os.path.isfile(path) or entry.startswith(".") or not dot:
                continue
            if ext.lower() not in EXTENSIONS:
                continue
            shutil.copy2(path, os.path.join(dest, entry))
            plans.append({
                "id": entry,
                "file": entry,
                "title": title_of(path, stem),
                "source": "%s/%s" % (SOURCE_DIR, entry),
                "bytes": os.path.getsize(path),
            })

    with open(os.path.join(dest, "manifest.json"), "w") as handle:
        json.dump({"plans": plans}, handle, indent=1)
    print("stage_plans: staged %d plan(s) into %s" % (len(plans), dest))


if __name__ == "__main__":
    main()
