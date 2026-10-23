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

The page (voice-1a2680b8, Jake's spec): the landing is the parts list beside the 3D view, and nothing else. The list is
the Generalist assembly top to bottom — Gripper, Handle, Base, Mount, Arm — one row per part showing the version it is at and a
selector to switch it to any other version of that part (AGENTS.md: each part counts on its own; the Aero Hand stays its own
family and is never a Generalist option). Under each row hang that part's own pieces with an eye to hide one (mesh.visible only,
so Open/Close and Explode keep moving it) and Only to isolate it. Open/Close and Explode float on the 3D view. The family
dropdown at the top of the list switches to the Aero Hand (its assembly: Aero Hand, Mount, Arm, the hand on the Mount's hub),
Glove Hand or Orca Hand; a family with no assembly lists its versions, tap one to see it alone.

Swapping a part can affect the others, so the list handles the dependencies (cad/mobile_gallery/model.js, buildMix): an adapter
part — the Mount to the arm, the Handle to the fingers — moves to the newest version that fits the new pick and says so under its
row ("✓ Mount 2 follows Arm 2."); any other part that no longer fits, or an adapter with no fitting version, gets a flag under the
affected row instead ("⚠ Base 3 has no wrist bracket (hand-held), so it does not fit Mount 1's tool plate."). Fit comes from the
catalog (fingers, carries, fits, tool_plate: Mount 2 takes Mount 1's tool plates), never from names. Nothing is ever switched off
for you: dropping the Mount under an Arm flags the Arm. The first load settles the adapters the same way, silently; a catalog
refresh never moves a pick. Picks: ?gripper=21&handles=6&base=none&mount=1&arm=1 presets them; #generalist-mix and #aero-mix
open an assembly, #<design id> opens one version alone (its first row returns to the assembly). Arm and Mount start off
(the arm dwarfs the gripper). Scripts/test_gallery.py checks the rows, the Aero Hand's absence and the dependency rules under
Node, and renders the landing page in headless Chrome through serve_designs.py.

Tune (Handle 4 on): a version whose folder has params.json + live_render.py publishes its parameters into the catalog (params)
and gets a Tune button on its row (or at the top of the list when it is shown alone). It shows that version alone with one
slider per parameter. Each change POSTs {design, values} to serve_designs.py /tune, which renders the real OpenSCAD parts into
tune/<id>/<hash>/ under the served directory (80 kept per design) and the view swaps them in. ?tune=name:value,... presets the
values; Copy puts the changed ones on the clipboard for the next version's params.json. This is the one place the server runs
CAD on request; values are numbers only, checked against params.json and clamped to slider range.

Hidden versions: hidden.json in the curated directory (design ids) keeps versions out of a family's side-by-side list. Only the
CLI writes it now: python3 Scripts/design_visibility.py hide gripper 1 2 | hide handle 3 | show base 1 | show all | list (through
serve_designs.py's one POST endpoint, JSON only, design ids only); publishing never touches it.

Exploded views use authored per-part offsets from the CAD export manifests. Version-folder projects can provide
viewer_parts.json with a parts array of {path, name, color, explode:[x,y,z]}; paths are relative to the version folder, STLs
retain assembled coordinates, and offsets are millimetres. A part's kind comes from its name before " — ": a handle says
"strap slide" or "handle", a finger says "finger", Arm/Mount/Aero Hand pieces are named for them (reBot Arm…, Wrist hub, Tool
plate, Aero Hand tool plate, Aero Hand (left)…) and the rest of a Base design is its base. Fingers that only exist inside a
later design come from the catalog's "fingers" field (VERSIONS.txt ", Gripper 21"). Open/Close moves parts by
cad/mobile_gallery/poses.js. ?open=0..100 and ?view=top|front|side|iso preset the pose and camera for screenshots.

Reference photo (voice-c68a1812): every design's parts list starts with a Reference photo row and an eye. On, the family's real
photo is one more tile beside the 3D view(s) (focused: the model and the photo side by side), with a picker for which photo; it
stays on across versions and families. reference/photos.js maps family -> photos (written by reference/make_reference.py, which
also resamples the top photo into gripper CAD millimetres); a family with none still shows the row, greyed ("No reference photo
yet"). Add a family's photos in make_reference.py and re-run it. ?photo=1 or ?photo=<id> (side, cup, ...) presets it on.

Average human hand (voice-bf770cd7): under the Reference photo row, an eye puts a proportionally accurate adult hand in every 3D
view (human_hand.js), fingertips level with the gripper's fingers, beside them in +X with the palm facing the gripper (its grasp
axis on the jaws' axis) or over them, see-through. Its controls hang under the row: size (ANSUR II mean hand length: adult
187 mm, man 193, woman 181), right or left, beside or over, Open/Close, a bend slider for all fingers and one per finger and the
thumb, and "Bend with the gripper's Open/Close" (on by default: the gripper's button bends the hand too). The mesh is the WebXR
Input Profiles generic hand (MIT); source, sizes and joint limits are in reference/human_hand/SOURCE.txt. GLTFLoader and
SkeletonUtils (three r185) are vendored under cad/compare/vendor/loaders and utils. ?hand=1|right|left presets it on, ?curl=0..100
its bend (Follow off), ?handsize=man|woman, ?handat=over|grip.

Holding the gripper (the third "where" choice, ?handat=grip): the hand holds the gripper the way the strap loops are meant
for (plans/crow_gripper.md): a right hand's index and middle along the right handle's outer face, its thumb along the left's,
palm resting on the top-plate side, ring and pinky curled; a left hand mirrors it. gripHand (human_hand.js) solves the hand's
place and turn, the index/middle bends and the thumb's joints by coordinate descent: the pads land on spots raycast onto each
handle's outer face 45 mm under its top, and no joint goes into the boxes of the base, top plate, servo or pinion (the arm, mount
and wrist bracket are ignored). It re-solves on every frame of the gripper's Open/Close (about 4 ms warm). A version without
handles is held by its fingers' outer edges. Scripts/test_gallery.py checks it under Node with the real hand: pads within 6 mm,
thumb and index on opposite handles, no joint inside the base, open, closed and left-handed.

Human thumb/index fit (voice-3f6ae8e1): Holding the gripper targets only actual attachment meshes, including Base 19's low Driver cradles; missing attachments produce a warning. It uses index/thumb contacts and fixes the wrist through Open/Close by default. Custom hand length, digit collision radius and contact station are exploratory assumptions. Check 13 stroke positions samples closed to open and Copy fit report copies the assumptions and diagnostics. Box overlap is conservative and pad miss is a local IK residual; neither certifies physical fit. Scripts/check_human_fit.py runs the same solver on four actual CAD assemblies; plans/human_hand_interface.md contains the measurements and saddle/retention proposal. No new part geometry or universal fit claim.
