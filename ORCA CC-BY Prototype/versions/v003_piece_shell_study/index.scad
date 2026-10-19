// v003 — ORCA index pieces with inward-distance cavity and inspection section.
// ORCA Dexterity, Inc. — CC BY 4.0; see LICENSE and README.txt.
// The exact source exterior is retained. The inner offset is a sampled mesh.
// Closed internal cavities are an inspection study, not a wearable passage.

/* [Inspection] */
part = "all"; // [all,AP,PP,IP]
geometry = "shell"; // [shell,original,cavity]
section = "half"; // [half,whole]
outer_scale = 1; // [1,2]
// Offset in ORIGINAL 1x millimeters. At 2x it doubles with the whole part.
wall_offset = 1.5; // [1.0,1.5,2.0]
// Section location in original millimeters; removes the near (-Y) side.
section_y = 0; // [-9:0.25:9]
// Labels are preview-only and are omitted from STL export.
show_labels = true;

/* [Hidden] */
$fn=64;
$vpt=[0,0,24*outer_scale];
$vpr=[75,0,25];
$vpd=(part=="all" ? 245 : 140)*outer_scale;
names=["I-AP-R","I-PP","I-IP"];
labels=["AP / base","PP / proximal","IP / distal"];
colors=[[0.35,0.54,0.72],[0.75,0.80,0.84],[0.94,0.64,0.28]];
function wall_tag(t) = t==1 ? "1.0" : t==1.5 ? "1.5" : "2.0";
assert(wall_offset==1 || wall_offset==1.5 || wall_offset==2,
       "Use an available wall_offset preset: 1, 1.5, or 2 mm.");
echo(str("Nominal inner offset at displayed scale: ",wall_offset*outer_scale," mm"));

// The same rigid transform is applied to each source and its offset cavity.
// These are display placements, not assembly transforms.
module placement(i) {
    if (i==0) translate([0,0,24.28112]) rotate([0,90,0]) children();
    if (i==1) translate([0,0,9.49683]) children();
    if (i==2) translate([0,0,7.5]) children();
}
module original(i) {
    placement(i) import(str("source/",names[i],".stl"));
}
module cavity(i) {
    placement(i) import(str("generated/",names[i],"_cavity_",wall_tag(wall_offset),"mm.stl"));
}
module chosen_geometry(i) {
    if(geometry=="original") original(i);
    else if(geometry=="cavity") cavity(i);
    else difference() { original(i); cavity(i); }
}
module inspected(i) {
    difference() {
        chosen_geometry(i);
        if(section=="half") translate([-100,section_y-200,-100]) cube([200,200,300]);
    }
}

for(i=[0:2]) if(part=="all" || part==["AP","PP","IP"][i]) {
    translate([part=="all" ? (i-1)*40*outer_scale : 0,0,0]) {
        // Resolve subtraction for a faithful F5 preview as well as F6/STL.
        color(colors[i]) scale(outer_scale) render(convexity=20) inspected(i);
        if(show_labels && $preview) color([0.25,0.28,0.31]) translate([0,-13*outer_scale,0])
            linear_extrude(0.3) text(labels[i],size=3.2*outer_scale,halign="center",valign="top");
    }
}
