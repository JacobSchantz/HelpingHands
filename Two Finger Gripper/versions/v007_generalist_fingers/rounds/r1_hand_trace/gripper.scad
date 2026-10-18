/* GENERALIST GRIPPER — GENERATION 7 / the two yellow fingers only, mm.
   Jake: "delete everything else, just keep the yellow grippers ... get the yellow part to
   look as close as possible to Generalist's yellow part." No body, mount, camera, straps,
   carriers, gears or drive. The outline is a pixel trace of the lower finger of the
   left-hand device in cad/reference/generalist_gripper_gen6_two_hands.png, mapped to mm
   below, so a re-trace is an edit to the px lists, nothing else.
   Axes: X across (right finger +X), Z along the fingers (tips +Z), +Y = dorsal. */
$fn=32;
part="assembly"; // assembly | left | right | collision | none | viewer_left | viewer_right
angle=15;        // each finger's swing about its pivot; 0 = closed (the photo pose)
max_angle=30;

// ---------- photo -> mm ----------
mm_per_px=0.2;            // ~110 mm pivot-to-tip; no measured scale, see README
px_pivot=[345,393];       // placeholder M3 pivot in the solid root lip
axis_deg=36.5;            // bisector of the two closed fingers in the photo (27 and 46 deg)
plate=12;                 // finger thickness along Y, centred on the hand plane
pivot_bore=3.2;
tip_gap=1.0;              // closed tip-to-tip gap

// finger frame (right finger): pivot at origin, inner (gripping) side is -X
function px(q)=let(d=q-px_pivot) mm_per_px*[-(d[0]*sin(axis_deg)-d[1]*cos(axis_deg)), d[0]*cos(axis_deg)+d[1]*sin(axis_deg)];
function pxs(l)=[for(q=l) px(q)];

outline_px=[
    // inner edge, root -> tip: gusset, bar, two step teeth, jaw
    [398,336],[412,340],[432,356],[455,380],[480,403],[510,425],[550,446],[590,458],[624,466],
    [630,473],[635,492],                                    // tooth 1
    [660,500],[694,509],
    [699,520],[705,532],                                    // tooth 2
    [730,541],[770,557],[805,573],[830,590],[846,603],[851,607],   // jaw to the point
    // outer edge, tip -> root: jaw, knee, bar (under the black carrier in the photo),
    // the slot the carrier tongue slides into, root lip
    [843,612],[805,607],[765,597],[725,584],[692,571],[668,557],[660,545],
    [650,531],[600,507],[550,483],[500,456],[450,432],[400,414],[399,405],[356,401],[353,410],
    [345,414],[326,411],[318,400],[321,387],[338,376],[360,362],[380,346]];
root_holes_px=[[385,355],[409,357],[375,379],[397,380],[422,379],[414,399],[436,399],[450,416],[467,416]];
dot_px=[727,559];         // the black dot at the start of the jaw
slots_from_px=[748,568];  // single row of slanted slots along the jaw
slots_to_px=[823,586];
slot_count=6;

tip=px(outline_px[20]);
pivot=-tip[0]+tip_gap/2;  // half the pivot spacing: closed tips sit tip_gap apart
root_hole_d=3.0;
cell=2.0;  cell_wall=0.7; rim=0.6;     // bar honeycomb: thin walls, as in the photo
pocket=3.5;               // blind pocket depth from each face; leaves a 5 mm web
bar_from=26; bar_to=68;   // finger-frame Z band of the bar honeycomb (root gusset .. knee)
bar_mid_px=[550,464];     // a point on the bar centreline: the lattice is centred on it
bar_lean=8.5;             // bar direction vs the axis, from the photo (28 vs 36.5 deg)

module profile() {polygon(pxs(outline_px));}
module root_holes2d() {for(q=root_holes_px) translate(px(q)) circle(d=root_hole_d);}
module slots2d() {
    a=px(slots_from_px); b=px(slots_to_px);
    for(i=[0:slot_count-1]) translate(a+(b-a)*i/(slot_count-1)) rotate(-35) hull()
        for(s=[-1,1]) translate([s*0.9,0]) circle(d=1.4,$fn=12);
}
module bar_cells2d() {
    // Two staggered rows along the bar, whole cells only: centres are kept where a full
    // cell fits inside the rim, then each centre is grown back into a round pocket.
    p=cell+cell_wall;
    minkowski() {
        intersection() {
            translate(px(bar_mid_px)) rotate(bar_lean) for(j=[-20:20],i=[-3:3]) translate([i*p*sqrt(3)/2,j*p+(abs(i)%2)*p/2]) square(0.02,center=true);
            offset(delta=-cell/2-rim) profile();
            translate([-40,bar_from]) square([80,bar_to-bar_from]);
            difference(){translate([-40,0]) square(200); for(q=root_holes_px) translate(px(q)) circle(d=root_hole_d+2*cell_wall+cell);}
        }
        circle(d=cell,$fn=12);
    }
}
module pockets2d() {root_holes2d();bar_cells2d();slots2d();translate(px(dot_px)) circle(d=2.6);}
module xz(h) {rotate([-90,0,0]) mirror([0,1,0]) linear_extrude(h,center=true) children();}
module finger() {
    difference() {
        xz(plate) profile();
        for(s=[-1,1]) translate([0,s*(plate/2-pocket/2+0.5),0]) xz(pocket+1) pockets2d();
        xz(plate+2) circle(d=pivot_bore);
    }
}
module placed(s=1,a=angle) {
    translate([s*pivot,0,0]) rotate([0,s*a,0]) if(s<0) mirror([1,0,0]) children(); else children();
}
module piece(q,a=angle) {
    if(q=="left") placed(-1,a) finger();
    if(q=="right") placed(1,a) finger();
}
module clash(a=angle) {intersection(){piece("left",a);piece("right",a);}}
assert(angle>=0&&angle<=max_angle,"Angle outside intended motion");
if(part=="assembly") color("#efb83b") {piece("left");piece("right");}
if(part=="right") color("#efb83b") finger();
if(part=="left") color("#efb83b") mirror([1,0,0]) finger();
if(part=="collision") clash();
for(q=["left","right"]) if(part==str("viewer_",q)) piece(q);
