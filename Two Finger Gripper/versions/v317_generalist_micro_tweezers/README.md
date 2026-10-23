# Base 16 + Gripper 23: miniature geared tweezers

Builds on Base 15's captured-post/plain-cap architecture and involute gear construction, and Gripper 22's supported pivot concept. This is a new miniature branch, not a scaled servo or a revision to an existing print.

Assumed servo: Feetech STS3215. Its narrowest case dimension is **24.8 mm**, from the repository's SO-ARM100 STEP-derived dimensions in Base 15. The 45.4 × 24.8 × 31.8 mm case is drawn as an envelope, not a detailed servo mesh.

- 24.8 mm maximum assembly width, including servo; fixed frame is 24.4 mm.
- Two 42 mm slender jaws with rounded 0.7 mm tips; about 13 mm opening at 9° per jaw.
- Equal 20-tooth involute gears, module 0.38, 20° pressure angle, opposite rotation at 1:1.
- Drive jaw sits over the servo axis. A low flange bolts to the stock 20 mm horn on its 14 mm four-hole circle; a D shaft transfers rotation through the fixed frame.
- Follower axle and cap supports belong to the base. The cap supports the follower and drive journal at their upper ends.
- Servo and hardware dimensions are not scaled. Base mounts through the existing four M2 case holes.
- Five printed parts: two geared jaws, base, cap, coupler. No handles or arm mount. This miniature interface cannot accept full-size Handles or Grippers 1–22; select Gripper 23 with Base 16.

## Assembly and limits

Fit the coupler to the horn before installing the base. Install the base's four case screws, seat both geared jaws at the closed-tip position (D drive left, plain bore right), then fit the cap with its two M2 screws. Verify actual screw lengths and thread engagement on hardware; screw heads and a conservative cable/plug bend zone are included in the envelope render. The four horn holes use the actual CAD’s 45° pattern, with countersunk screws flush in the coupler. The centre screw has 2.2 mm of underside relief. Confirm head diameter, screw lengths and engagement on the actual servo.

The module-0.38 teeth and narrow jaws are a **light-load CAD prototype**, intended for fine resin printing or machining. Ordinary FDM is unlikely to resolve the teeth reliably. Printed 2 mm follower posts, material strength, backlash, wear and servo torque limits need physical tests. Do not apply the servo's full stall torque. This model does not prescribe a tested safe torque or payload.

The physical servo can rotate farther than the commanded stroke. Set and verify software limits to 0–9° from the calibrated closed pose before fitting the jaws; no hard stops are claimed. The all-width statement applies to this commanded stroke, not unrestricted motor motion.

## Checks and reproduction

Run python3 export_models.py, python3 genus.py, then python3 check_geometry.py in this folder. OpenSCAD is required.

Ten exported component/reference meshes are closed manifolds with positive volume. The geometry check tests the actual left/right jaws and coupler every 0.5° across 0–9°, checks the fixed frame/cap/servo bounds, and uses solid intersections to check jaw-to-jaw, moving-to-frame and moving-to-fastener interference. A separate analytic calculation finds each triangle vertex’s extrema over the continuous stroke, including the hardware and cable envelopes; width compliance does not depend on the 0.5° sample spacing. An excessive 40° opening must fail the same envelope calculation. Tune variants also reject a width violation. Reports are mesh_checks.json and geometry_checks.json.

The complete commanded stroke fits in the servo's width in CAD. This is not print-tolerance, hardware-fit or strength verification. params.json contains every physical dimension and its source/meaning.
