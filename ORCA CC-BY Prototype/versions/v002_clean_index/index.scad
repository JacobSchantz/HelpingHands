// ORCA index finger — v002 clean intact reference, original scale (mm).
// ORCA Hand by ORCA Dexterity, Inc. — CC BY 4.0; see LICENSE.
// Three original manufacturing parts, rigid placement only. No cut or enlargement.
// Pins, bearings, tendon and skin are not included. Placement evidence: v001 snapshot.
$vpt=[0,0,30];
$vpr=[74,0,35];
$vpd=340;
color([0.80,0.84,0.88]) {
    rotate([0,90,0]) import("source/I-AP-R.stl");
    import("source/I-PP.stl");
    translate([1.5,0,37]) import("source/I-IP.stl");
}
