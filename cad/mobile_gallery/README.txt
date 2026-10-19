HelpingHands project Live Preview

Open HelpingHands > Live Preview in Pebbles. The existing private embedded Tailscale route proxies this Mac's loopback port8768. A public Funnel is not required. A normal external browser needs its own tailnet access; use Pebbles on the phone.

The gallery reads catalog.json and displays actual OpenSCAD STL exports, including incomplete work and archived versions. It does not recreate the design in JavaScript. New working versions are discovered by Scripts/publish_designs.py. Keep main SCAD files in the project's numbered versions folder with dependencies alongside them; see that script's discovery rules. Helper/source meshes are not presented as assembled designs.

Scripts/serve_designs.py serves ONLY the curated HelpingHands-tools/design-gallery directory on127.0.0.1:8768 and invokes the publisher every300seconds after the preceding run completes. It never serves the repository or home directory. The browser checks the catalog every300seconds and offers a manual refresh button (which reads the current catalog; it does not execute CAD).

Installed user launch agent: ~/Library/LaunchAgents/com.helpinghands.design-preview.plist
Service label: com.helpinghands.design-preview
Log: ~/HelpingHands-tools/design-preview.log
Manual export: python3 Scripts/publish_designs.py
Manual server: python3 Scripts/serve_designs.py

On export failures, retained successful artifacts remain available and the catalog reports the error. Catalog time and last successful model export time are separate. New source versions can appear before any successful mesh exists. Source bundles retain available attribution and licenses.

Live remote access requires this Mac to be awake, online and logged in. This is not cloud hosting or guaranteed offline synchronization. Physical-phone rendering must be verified on the phone; desktop mobile-viewport tests alone cannot establish it.

The default view compares all generations for the selected family as interactive
3D viewports. Tap a generation to focus; All returns to comparison. The one top
row contains the family selector and refresh. A floating bottom-right
Explode/Assemble button appears when positioned parts are available. There is no bottom metadata panel. Double-click a model
to frame it; drag to orbit and pinch to zoom.

Exploded views use authored per-part offsets from the CAD export manifests.
Version-folder projects can provide viewer_parts.json with a parts array of
{path, name, color, explode:[x,y,z]}; paths are relative to the version folder,
STLs retain assembled coordinates, and offsets are millimetres. Single merged
assemblies without part metadata are not arbitrarily split or displaced.

Hiding generations: the header's "Hide…" button (it reads "2 hidden" once some are) opens a checklist of the selected family's generations. Unchecked ones drop out of the comparison on every device. The list is hidden.json in the curated directory, saved through serve_designs.py's one POST endpoint (JSON only, design ids only); publishing never touches it. Voice/CLI: python3 Scripts/design_visibility.py hide gripper gen 1 2 | show gripper gen 1 | show all | list

Actual (Generalist): the Generalist Gripper family gets an extra first tile, the real gripper. Its default photo is the left device of cad/reference/generalist_gripper_gen6_two_hands.png resampled into the gripper's CAD millimetres (the same photo->mm frame Gens 9-11 were traced in) and laid on the Y=0 plane; the tile's dropdown swaps to the other reference photos, shown flat. Regenerate with python3 cad/mobile_gallery/reference/make_reference.py. It hides like any generation (id generalist-actual).

Top / Front / Side / Iso (bottom right) snap every tile on screen to one camera: same direction, centre and scale, framed on all shown models together. Top is the photo's viewpoint and also closes the jaws to the photo's pose. ?view=top does the same once the models load.
