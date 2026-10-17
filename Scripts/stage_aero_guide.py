#!/usr/bin/env python3
"""Stage the Aero Hand build guide into the built app bundle.

Run as a build phase. Mirrors third_party/aero_hand/guide/ into
<bundle>/AeroGuide/ so the in-app gallery (index.html) and the assembly PDF
open offline. Rendered page images (p<n>.png, gitignored, made by
render_pages.py) are shrunk to 1600 px on the way in to keep the install
small. Files are only re-copied when the source is newer, so incremental
builds stay fast.
"""
import os
import shutil
import subprocess
import sys

SOURCE_DIR = "third_party/aero_hand/guide"
# Desk-only tooling and source photos the pages never load.
SKIP = {".gitignore", "go.sh", "guide_server.py", "render_pages.py", "current", "helper", "raw", "__pycache__"}
PAGE_MAX_PX = "1600"


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
        sys.stderr.write("stage_aero_guide: no BUILT_PRODUCTS_DIR — pass a destination\n")
        sys.exit(2)
    return os.path.join(products, resources, "AeroGuide")


def is_page_image(name):
    stem, _, ext = name.rpartition(".")
    return ext == "png" and stem[:1] == "p" and stem[1:].isdigit()


def stale(src, dst):
    return not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src)


def stage(src, dst):
    if is_page_image(os.path.basename(src)):
        result = subprocess.run(["sips", "-Z", PAGE_MAX_PX, src, "--out", dst],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if result.returncode == 0:
            return
    shutil.copy2(src, dst)


def main():
    source = os.path.join(repo_root(), SOURCE_DIR)
    dest = destination()
    if not os.path.isdir(source):
        print("stage_aero_guide: no %s — skipping" % SOURCE_DIR)
        return

    wanted, copied = set(), 0
    for folder, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith(".")]
        rel = os.path.relpath(folder, source)
        out = os.path.normpath(os.path.join(dest, rel))
        os.makedirs(out, exist_ok=True)
        for name in files:
            if name in SKIP or name.startswith("."):
                continue
            src, dst = os.path.join(folder, name), os.path.join(out, name)
            wanted.add(os.path.normpath(dst))
            if stale(src, dst):
                stage(src, dst)
                copied += 1

    # Drop anything removed from the guide since the last build.
    for folder, _, files in os.walk(dest):
        for name in files:
            path = os.path.normpath(os.path.join(folder, name))
            if path not in wanted:
                os.remove(path)

    print("stage_aero_guide: %d file(s) in %s (%d updated)" % (len(wanted), dest, copied))


if __name__ == "__main__":
    main()
