// label: index finger, first test print
// gen_04 · the gen_03 index finger made printable (voice-55a7493e, Jake
// 2026-10-17: gen_03 is a useful mechanism but not accepted; keep going until
// a FIRST TEST PRINT is ready). gen_03 stays as it was. Never edit a
// generation once a newer one exists: copy it to the next number.
//
// Original geometry from our own requirements and jake_hand.scad's numbers
// (read with jake(), never copied or changed). REFERENCES.md lists the ideas.
// No CAD from any other hand was used.
//
// What changed from gen_03, and why (compare/gen_04.md has the numbers):
//   middle finger - every saddle stays inside Jake's own index width on the
//             ulnar side (x >= -skin half-width), and every hinge is on the
//             radial side. Nothing rigid sits between the index and middle
//             fingers, so they can stay together and move independently.
//   thumb   - the base's radial hardware is a slim strut, no bridge block;
//             the drum moved up over the dorsum. Clear from thumb_yaw ~40
//             (the check measures it); the adducted photo pose (22) still
//             hits, because a coaxial MCP hinge needs room beside the knuckle.
//   MCP     - a real flexion stop: a tail on the proximal tab swings up into
//             a block on the base at ~95 deg. The same block stops
//             hyperextension.
//   hinges  - PIP and DIP are radial clevises (distal saddle forks round a
//             lug on the proximal one), one 1.75 mm filament pin, pressed in
//             the fork and running in the lug. MCP is one M3x6 bolt through
//             the tab into a tapped plate, head outside.
//   print   - saddles are a flat-topped section (top, 45 deg corners, radial
//             wall), printed top-down with no supports. The elastic runs in
//             a channel inside the top. The base prints upright with
//             supports under its pad; drum and coupon print flat.
//   drum    - turned by hand: axle along x (an M3x20 bolt) on one cheek, a
//             1.75 mm pin through the cheek into one of 24 holes locks it.
//             No servo horn: that waits for the real servo.
//
// Frame: as gen_03. Built about the index MCP axis ("local": origin on the
// axis, x along it toward the thumb, y along the finger at 0 deg, z to the
// back of the hand) and placed in jake_hand.scad's frame with tr(M).
//
// part = assembly | poses | base | proximal | middle | distal | drum | coupon
//      | parts | print (piece = base | proximal | middle | distal | drum | coupon:
//        that part in its print orientation; print_gen_04.py drops it on z = 0)
//      | check (pair = [a, b]) | path
use <jake_hand.scad>

part = "assembly";
bend = [0, 0, 0];        // MCP, PIP, DIP flexion, degrees
pair = ["base", "proximal"];
piece = "base";
guides = true;           // false: leave the cord guides off (the cord-clearance check)

/* [Neighbours, for the check: the photo pose is splay 0, thumb yaw 22] */
middle_splay = 0;
middle_flex = [0, 0, 0];
thumb_yaw = 45;
thumb_flex = [0, 0];
neighbour_grow = 0;      // the neighbours are checked as skin

/* [Fit: as gen_02/03] */
clearance = 1.5;         // comfort gap all round the finger and palm
tip_room = 3;
nose_floor = 2;          // the fingertip cap's underside, below the finger's centreline

/* [Joints] */
limit = [90, 100, 70];   // MCP, PIP, DIP flexion range the check samples
vee = [0, 95, 62];       // V cut at the PIP and DIP ends (stop lands ~4-8 deg past it)
gap = 1.2;               // dorsal gap between saddles at 0 deg
shell = 1.6;             // PETG wall over the comfort surface
corner = 2.4;            // the 45 deg corner faces stand this far off the comfort surface
top_t = 4.8;             // top plate over the comfort surface (elastic channel inside)
flap_low = 0.85;         // radial wall reaches this share of the half-thickness below the axis
ulnar_wall = 1.2;        // thinnest ulnar edge kept
lug_r = 4;               // PIP and DIP hinge discs
fork_t = 1.6;            // the distal saddle's inner and outer fork plates
lug_t = 2;               // the proximal saddle's lug
lug_c = 0.3;             // running clearance between plates
pin_fix = 1.8;           // 1.75 mm filament pin, pressed in the fork
pin_run = 2.0;           // ... and running in the lug
mcp_r = 5.5;             // MCP discs
mcp_plate = 3.5;         // the base's MCP plate (inner), tapped for the M3 bolt
mcp_tab = 2.2;           // the proximal saddle's MCP tab (outer)
mcp_tap = 2.5;           // M3 self-tapping hole in the plate
mcp_run = 3.3;           // M3 running hole in the tab
tail_r = 8.5;            // the tab's tail: hits the stop block at MCP flexion
tail_w = 1.75;           // half-width of the tail
stop_y = 2.4;            // the stop block's back face (sets the MCP flexion stop)
prox_start = 15;         // the proximal saddle starts past the knuckle dome

/* [Tendon] */
cord_low = [8.5, 6.5, 5.5]; // below the MCP, PIP, DIP axis: the lever arm at 0 deg
cord_reach = [15, 12, 8];   // guides this far either side of each joint
cord_d = 1;                 // 1 mm braided PE line
cord_hole = 1.6;
boss_d = 4.0;
boss_len = 4;
cord_x = 13.6;              // the line's plane behind the MCP (post and drum groove)
post_at = [-9, -5.5];       // the turning post behind the MCP (y, z), axis along x
post_r = 2.5;

/* [Return elastic] */
elastic_d = 2;              // 2 mm round elastic
elastic_hole = 2.6;

/* [Base and drum] */
thumb_clear = [35, 85];     // the base is cut clear of the thumb (comfort volume) over this yaw range
base_back = 60;             // the base runs this far behind the MCP axis
pad = 2.4;                  // base shell over the palm comfort surface
pad_ulnar = -15;            // the base's ulnar edge, local x
strap = 20.5;               // palm strap slot (20 mm hook-and-loop)
finger_strap = 10.2;        // the proximal saddle's strap slot (10 mm hook-and-loop)
drum_at = [-25, 29];        // drum axle, local y and z (axis along x)
drum_r = 8;                 // line drum
drum_w = 6;                 // groove width
flange = [12.2, 12.5];          // ulnar flange (lock holes) and radial flange (knob) radii
flange_t = 2;
lock_r = 9.8;               // the 24 lock holes
lock_n = 18;
cheek_t = 6;
axle = 3.3;                 // M3x20 bolt + nyloc

$fn = 32;

// ---------- the finger, from jake_hand.scad ----------

F = 0;
M = hand_mcp(F);
Lp = jake("finger_len")[F] * jake("phalanx");
W = lerp4(jake("finger_base_w")[F], jake("finger_tip_w")[F]);
T = lerp4(jake("finger_base_t")[F], jake("finger_tip_t")[F]);
E = [Lp[0], Lp[1], Lp[2] - min(W[3], T[3]) / 2 + tip_room];   // joint to joint, as hand_finger()
g = clearance;

function lerp4(a, b) = [for (k = [0:3]) a + (b - a) * k / 3];
function tr(v) = [[1, 0, 0, v[0]], [0, 1, 0, v[1]], [0, 0, 1, v[2]], [0, 0, 0, 1]];
function rx(a) = [[1, 0, 0, 0], [0, cos(a), -sin(a), 0], [0, sin(a), cos(a), 0], [0, 0, 0, 1]];
function at(m, p) = let(q = m * [p[0], p[1], p[2], 1]) [q[0], q[1], q[2]];

function frame(k, b = bend) = k == 0 ? rx(-b[0]) : frame(k - 1, b) * tr([0, E[k - 1], 0]) * rx(-b[k]);

function half(k, y, extra) = let(f = max(0, min(1, y / E[k])))
    [(W[k] + (W[k + 1] - W[k]) * f) / 2 + extra, (T[k] + (T[k + 1] - T[k]) * f) / 2 + extra];
function side(k, y, z, extra) = let(h = half(k, y, extra)) h[0] * sqrt(max(0, 1 - pow(z / h[1], 2)));
function low(k) = flap_low * (T[k] + T[k + 1]) / 4;
function xi(j) = W[j] / 2 + g + 0.1;          // inner face of the hinge stack at joint j
function chan_z(k, y) = half(k, y, g)[1] + top_t / 2;   // the elastic channel's centre
function elastic_exit() = E[2] - 3;                      // where it turns up out of the distal saddle

module finger(grow, b = bend) hand_finger(F, grow, tip_room, b);
module segment(k, grow) hand_segment(E[k], W[k], T[k], W[k + 1], T[k + 1], grow);
module palm_local(grow) translate(-M) hand_palm(grow);

// In the y-z plane, extruded along x: the layer [x0, x0 + th] on the radial side.
module layer(x0, th) translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(th) children();

// ---------- saddles ----------

// Saddle k's outside at y, in the x-z plane: a flat top top_t over the
// comfort surface, 45 deg corners `corner` off it, a flat radial wall down to
// low(k), and on the ulnar side nothing past Jake's own skin (x >= -w/2).
function section(k, y) = let(h = half(k, y, g), A = h[0], B = h[1], wh = half(k, y, 0)[0],
        zt = B + top_t, xr = A + shell, c = sqrt(A * A + B * B) + sqrt(2) * corner,
        zu = B * sqrt(max(0, 1 - pow((wh - ulnar_wall) / A, 2))))
    [[xr, -low(k)], [xr, c - xr], [c - zt, zt], [-(c - zt), zt], [-wh, c - wh], [-wh, zu], [0, -low(k)]];
module slab(k, y) translate([0, y, 0]) rotate([90, 0, 0]) linear_extrude(0.01, center = true) polygon(section(k, y));

// What saddle k keeps along y (in the y-z plane): above the axis the ends are
// square, gap/2 off the joint; below it they lean back by half of vee, so the
// two faces meet near the joint's flexion limit (the hard stop).
module keep2d(k) let(y0 = k == 0 ? prox_start : gap / 2, y1 = k == 2 ? E[2] + 30 : E[k] - gap / 2,
                     Z = 40, a = k == 0 ? 0 : vee[k] / 2, d = k == 2 ? 0 : vee[k + 1] / 2)
    polygon([[y0, 40], [y0, 0], [y0 + Z * tan(a), -Z], [y1 - Z * tan(d), -Z], [y1, 0], [y1, 40]]);

// Cord guides stand just outside the flat radial wall, so the line runs in
// the open between them.
function guide_at(k, y, z) = [half(k, y, g)[0] + shell + 0.7, y, z];
module tube(p, len = boss_len, v = [0, 1, 0], d = boss_d, hole = cord_hole)
    translate(p) rotate([0, acos(v[2] / norm(v)), atan2(v[1], v[0])]) difference() {
        cylinder(d = d, h = len, center = true);
        cylinder(d = hole, h = len + 1, center = true);
        // a 0.4 mm chamfer at each mouth, so the line turns over a rounded edge
        for (s = [-1, 1]) translate([0, 0, s * (len / 2 - 0.2)]) scale([1, 1, s]) cylinder(d1 = hole, d2 = hole + 0.8, h = 0.41, center = true);
    }
function guides_on(k) = k == 0 ? [[cord_reach[0], cord_low[0]], [E[0] - cord_reach[1], cord_low[1]]]
                      : k == 1 ? [[cord_reach[1], cord_low[1]], [E[1] - cord_reach[2], cord_low[2]]]
                      : [[cord_reach[2], cord_low[2]]];   // the distal one is the anchor

// Saddle k's body: sections hulled along y, the tip nose on the distal one.
module saddle_body(k) let(y0 = k == 0 ? prox_start : 0, y1 = k == 2 ? E[2] : E[k])
    hull() {
        slab(k, y0);
        slab(k, y1);
        if (k == 2) let(r = min(W[3], T[3]) / 2 + g + shell)
            translate([0, r + 1, 0]) scale([0.68, 1, 0.68]) slab(2, E[2]);
    }

// The radial clevis at joint j (between saddle j-1 and j), in its layers:
// the distal saddle's fork (inner plate = its own wall, outer plate) and the
// proximal saddle's lug between them.
function fork_in(j) = xi(j);
function lug_x(j) = xi(j) + fork_t + lug_c;
function fork_out(j) = lug_x(j) + lug_t + lug_c;
function stack_out(j) = fork_out(j) + fork_t;

function top_z(k, y) = half(k, y, g)[1] + top_t;    // the flat top (the print bed face) at y
// Where the comfort surface leaves a feather edge against a flat face, cut
// it square: the lip under the radial wall (inside x_lip, below z_lip) and
// the ulnar sliver below the ulnar edge's flat bottom.
function x_lip(k, y) = let(h = half(k, y, g + 0.1)) h[0] * sqrt(max(0, 1 - pow(low(k) / h[1], 2))) + 1;
function z_lip(k, y) = let(h = half(k, y, g + 0.1)) -h[1] * sqrt(max(0, 1 - pow(x_lip(k, y) / h[0], 2)));
function z_ulnar(k, y) = section(k, y)[5][1];
module trims(k) let(y0 = k == 0 ? prox_start - 1 : -1, y1 = E[k] + (k == 2 ? 0 : 1)) {
    hull() for (y = [y0, y1]) translate([0, y, 0]) rotate([90, 0, 0])
        linear_extrude(0.01, center = true) polygon([[0, -40], [x_lip(k, min(y, E[k])), -40], [x_lip(k, min(y, E[k])), z_lip(k, min(y, E[k]))], [0, z_lip(k, min(y, E[k]))]]);
    hull() for (y = [y0, y1]) translate([0, y, 0]) rotate([90, 0, 0])
        linear_extrude(0.01, center = true) polygon([[-40, -40], [0, -40], [0, z_ulnar(k, min(y, E[k]))], [-40, z_ulnar(k, min(y, E[k]))]]);
}
// Everything below the flat top (the print bed face), extended past both ends.
module below_top(k) let(y0 = k == 0 ? prox_start : 0, s = (top_z(k, E[k]) - top_z(k, y0)) / (E[k] - y0))
    hull() for (y = [y0 - 30, E[k] + 40]) translate([-60, y, -60]) cube([120, 0.01, 60 + top_z(k, y0) + s * (y - y0)]);

module saddle(k) {
    intersection() { saddle_raw(k); below_top(k); }
}
module saddle_raw(k) {
    difference() {
        union() {
            difference() {
                intersection() {
                    saddle_body(k);
                    rotate([90, 0, 90]) linear_extrude(120, center = true) keep2d(k);
                }
                trims(k);
                // the nose stops above the fingertip's pad: a square underside
                if (k == 2) translate([-30, E[2], -40]) cube([60, 30, 40 - nose_floor]);
            }
            // (the distal one is the line's anchor: a fatter boss round its knot pocket)
            if (guides) for (q = guides_on(k)) tube(guide_at(k, q[0], -q[1]), d = k == 2 ? 5.6 : boss_d);
            // MCP tab (outer layer), with the tail that meets the stop block
            if (k == 0) {
                layer(xi(0) + mcp_plate + lug_c, mcp_tab) difference() {
                    union() {
                        hull() { circle(r = mcp_r); translate([prox_start + 3, -mcp_r]) square([1, 2 * mcp_r]); }
                        translate([-tail_r, -tail_w]) square([tail_r, 2 * tail_w]);
                    }
                    circle(d = mcp_run);
                }
                // and its bridge in to the saddle wall, clear of the plate
                layer(xi(0) - 1.5, mcp_plate + lug_c + 1.6) translate([prox_start, -mcp_r]) square([4, 2 * mcp_r]);
            }
            // the fork at this saddle's proximal joint (PIP, DIP)
            if (k > 0) {
                // inner plate: the disc, joined to the wall (trimmed to its V)
                layer(fork_in(k), fork_t) difference() {
                    union() {
                        circle(r = lug_r);
                        intersection() { hull() { circle(r = lug_r); translate([lug_r + 3, -lug_r]) square([1, 2 * lug_r]); } keep2d(k); }
                    }
                    circle(d = pin_fix);
                }
                // outer plate: the disc, up to a tall plate that meets the top
                // plane, so it grows from the print bed
                layer(fork_out(k), fork_t) difference() {
                    hull() { circle(r = lug_r); translate([lug_r + 3, -lug_r]) square([3, lug_r + top_z(k, lug_r + 4.5) + 2]); }
                    circle(d = pin_fix);
                }
                // the bridge from the outer plate in to the wall, forward of the lug's reach
                layer(fork_in(k) - 1, stack_out(k) - fork_in(k) + 1) translate([lug_r + 3, -lug_r]) square([3, lug_r + top_z(k, lug_r + 4.5) + 2]);
            }
            // the lug at this saddle's distal joint
            if (k < 2) {
                j = k + 1;
                layer(lug_x(j), lug_t) difference() {
                    union() {
                        translate([E[k], 0]) circle(r = lug_r);
                        // behind the disc, up to the top plane (it grows from the bed)
                        translate([E[k] - lug_r - 5, -lug_r]) square([lug_r + 5, lug_r + top_z(k, E[k] - 4) + 2]);
                    }
                    translate([E[k], 0]) circle(d = pin_run);
                }
                // the bridge from the lug in to the wall, behind the fork's sweep
                layer(xi(j) - 1, lug_x(j) - xi(j) + 1 + 0.01) translate([E[k] - lug_r - 5, -lug_r])
                    square([3, lug_r + top_z(k, E[k] - 7.5) + 2]);
            }
        }
        // room for the next saddle's fork plate to turn in this saddle's wall
        if (k < 2) translate([0, E[k], 0]) layer(0, xi(k + 1) + fork_t + lug_c) circle(r = lug_r + lug_c);
        // the comfort surface (+0.1 so no face is shared with the check's comfort volume)
        segment(k, g + 0.1);
        // ... and the segment behind it (the palm, for the proximal saddle) at every
        // angle of the joint between them, so a saddle's corner never swings into it
        for (a = [-5 : 5 : limit[k] + 5]) multmatrix(rx(a))
            if (k == 0) palm_local(g + 0.1); else translate([0, -E[k - 1], 0]) segment(k - 1, g + 0.1);
        // the elastic channel along the top
        let(y0 = k == 0 ? prox_start : 0) hull() for (y = [y0 - 2, k == 2 ? elastic_exit() : E[k] + 2])
            translate([0, y, chan_z(k, y)]) rotate([90, 0, 0]) cylinder(d = elastic_hole, h = 0.01, center = true);
        // on the distal saddle the channel turns up through the top, with a
        // countersink for the knot
        if (k == 2) translate([0, elastic_exit(), chan_z(2, elastic_exit())]) {
            cylinder(d = elastic_hole, h = 20);
            translate([0, 0, top_z(2, elastic_exit()) - chan_z(2, elastic_exit()) - 1.6]) cylinder(d1 = elastic_hole, d2 = 5, h = 1.61);
        }
        // finger strap: a slot low in the proximal saddle's radial wall, between
        // its guides, for 10 mm hook-and-loop that goes under the finger and round
        // the saddle's top. (The middle saddle is too short for a slot between its
        // guides: a band goes round it, see the README.)
        if (k == 0) let(y = (cord_reach[0] + E[0] - cord_reach[1]) / 2 - finger_strap / 2)
            translate([x_lip(0, y) - 1, y, -low(0) + 1.6]) cube([10, finger_strap, 1.8]);
        // the knot pocket behind the anchor
        if (k == 2) let(p = guide_at(2, cord_reach[2], -cord_low[2]))
            translate(p + [0, boss_len / 2 - 1.4, 0]) rotate([-90, 0, 0]) cylinder(d = 3, h = 3);
    }
}

module saddle_at(k, b = bend) multmatrix(frame(k, b)) saddle(k);

// ---------- base ----------

plate_x = xi(0);                          // the MCP plate's inner face
tab_x = xi(0) + mcp_plate + lug_c;        // the tab's inner face
pad_top_front = 23;                       // local z of the elastic eyelet over the knuckle
module plate2d() union() {
    hull() { circle(r = mcp_r); translate([-10, 6]) square([12, 9]); }
    // forward, to carry the stop block
    translate([0, mcp_r + 0.6]) square([9.5, 4.9]);
    // the post's web: the line wraps the post's back and bottom, so it hangs off the front
    hull() { translate(post_at) circle(r = post_r); translate([-4.5, -2]) square([2, 2]); }
}

module base() difference() {
    union() {
        intersection() {
            difference() { palm_local(g + pad); palm_local(g); }
            // the pad's footprint narrows behind the drum, clear of the thumb's web
            translate([0, 0, 4]) linear_extrude(40) polygon([[pad_ulnar, -base_back], [pad_ulnar, 2], [plate_x + 0.5, 2],
                [plate_x + 0.5, -36], [-1, -46], [-1, -base_back]]);
        }
        layer(plate_x, mcp_plate) plate2d();
        // from the plate's top in to the pad, above the tab's tail
        translate([6, -10, 9.5]) cube([plate_x + mcp_plate - 6, 12, 5.5]);
        // the stop block, in the tab's layer: the tab's top edge lands on it at
        // MCP hyperextension, its tail at MCP flexion
        layer(plate_x + mcp_plate - 0.01, mcp_tab + lug_c + 0.01) translate([stop_y, mcp_r + 0.6]) square([9.5 - stop_y, 4.9]);
        // the turning post
        translate([12.2, post_at[0], post_at[1]]) rotate([0, 90, 0]) cylinder(r = post_r, h = plate_x + mcp_plate - 12.2);
        // elastic eyelet over the knuckle, anchor post at the back
        translate([0, -1.5, pad_top_front]) tube([0, 0, 0], 4, [0, 1, 0], 5.2, elastic_hole);
        translate([-2.6, -1.5, 18]) cube([5.2, 2, pad_top_front - 18]);
        translate(anchor_at()) cylinder(d = 4, h = elastic_anchor_z() + 3);
        translate(anchor_at() + [0, 0, elastic_anchor_z() + 3]) cylinder(d = 7, h = 1.5);
        // the drum's cheek
        let(x0 = drum_x0() - 0.3 - cheek_t) {
            hull() {
                translate([x0, drum_at[0], drum_at[1]]) rotate([0, 90, 0]) cylinder(r = flange[0] + 0.5, h = cheek_t);
                translate([x0, drum_at[0] - 9, 12]) cube([cheek_t, 18, 1]);
            }
        }
    }
    for (b = [-5 : 5 : limit[0] + 10]) finger(g, [b, 0, 0]);
    palm_local(g);
    // the thumb's comfort volume over its documented wearable range, straight and curled
    for (y = [thumb_clear[0] : 5 : thumb_clear[1]]) translate(-M) {
        hand_thumb(g, 0, y, [0, 0]);
        hand_thumb(g, 0, y, [30, 30]);
    }
    layer(plate_x - 0.01, mcp_plate + 0.02) circle(d = mcp_tap);
    // room for the tab and its tail to turn
    layer(tab_x - lug_c, mcp_tab + 2 * lug_c) difference() {
        circle(r = tail_r + 0.8);
        translate([stop_y, mcp_r + 0.6]) square([9.5 - stop_y, 4.9]);
    }
    // the axle and the lock-pin hole through the cheek
    translate([-10, drum_at[0], drum_at[1]]) rotate([0, 90, 0]) cylinder(d = axle, h = 40);
    translate([-10, drum_at[0], drum_at[1] + lock_r]) rotate([0, 90, 0]) cylinder(d = pin_run, h = 40);
    // the nyloc's hex, sunk in the cheek's ulnar face
    translate([drum_x0() - 0.3 - cheek_t - 0.01, drum_at[0], drum_at[1]]) rotate([0, 90, 0]) cylinder(d = 6.4, h = 2.4, $fn = 6);
    // palm strap: 20 mm hook-and-loop through this slot, round the palm and
    // back over the pad's radial edge, folded back on itself
    translate([pad_ulnar + 1.5, -base_back + 3, 0]) cube([2.2, strap, 60]);
}
function elastic_anchor_z() = 28;
function anchor_at() = [-4, -base_back + 5, 0];   // the elastic's anchor post   // local z of the anchor post's head (above the pad at the back)

// ---------- drum ----------

function drum_x0() = cord_x - drum_w / 2 - flange_t;    // the ulnar flange's ulnar face
module drum2() {   // in the local frame, axis along x
    translate([drum_x0(), drum_at[0], drum_at[1]]) rotate([0, 90, 0]) drum_flat();
}
// The drum on its own, axis along +z, ulnar flange on z = 0: its print pose.
module drum_flat() difference() {
    union() {
        cylinder(r = flange[0], h = flange_t);
        cylinder(r = drum_r, h = flange_t + drum_w);
        translate([0, 0, flange_t + drum_w]) difference() {
            cylinder(r = flange[1], h = flange_t + 1);
            for (a = [0 : 30 : 359]) rotate([0, 0, a]) translate([flange[1] + 0.6, 0, -1]) cylinder(r = 1.4, h = 5);
        }
    }
    translate([0, 0, -1]) cylinder(d = axle + 0.1, h = 20);
    for (a = [0 : 360 / lock_n : 359]) rotate([0, 0, a]) translate([lock_r, 0, -1]) cylinder(d = pin_run, h = flange_t + 2);
    // the line's end: out through the knob just above the core, knotted on
    // the knob's outer face in a countersink
    rotate([0, 0, 360 / lock_n / 2]) translate([drum_r + cord_hole / 2 + 0.3, 0, flange_t + drum_w - 0.5]) {
        cylinder(d = cord_hole, h = 10);
        translate([0, 0, flange_t + 1.5 - 0.99]) cylinder(d1 = cord_hole, d2 = 3.6, h = 1);
    }
}

// ---------- pin and clearance coupon ----------

// One bar printed in the saddles' pose (pin holes horizontal), with the
// candidate pin holes, and a comb of slots for a 2 mm tab at three clearances,
// plus the M3 holes. Notches on the top edge count the hole, left to right.
coupon_holes = [1.7, 1.8, 1.9, 2.0, 2.1, 2.5, 3.3];
coupon_slots = [0.2, 0.3, 0.4];
module coupon() {
    difference() {
        cube([8 * len(coupon_holes) + 4, 8, 8]);
        for (i = [0 : len(coupon_holes) - 1]) {
            translate([4 + 8 * i + 2, -1, 4]) rotate([-90, 0, 0]) cylinder(d = coupon_holes[i], h = 10);
            for (n = [0 : i]) translate([4 + 8 * i + 0.4 + 1.2 * n, -1, 7.4]) cube([0.6, 10, 1]);
        }
    }
    translate([0, 12, 0]) difference() {
        cube([10 * len(coupon_slots) + 4, 8, 8]);
        for (i = [0 : len(coupon_slots) - 1]) {
            translate([4 + 10 * i, -1, 2]) cube([lug_t + 2 * coupon_slots[i], 10, 7]);
            for (n = [0 : i]) translate([4 + 10 * i + 4 + 1.2 * n, -1, 7.4]) cube([0.6, 10, 1]);
        }
    }
    // the tab that goes in the slots, with a running pin hole
    translate([0, 24, 0]) difference() {
        cube([24, 8, lug_t]);
        translate([20, 4, -1]) cylinder(d = pin_run, h = 4);
    }
}

// ---------- the line and the elastic (drawn, not printed) ----------

// Internal tangent from the post (the line on its back) to the drum (the line
// on its front): [point on post, point on drum], in the y-z plane.
function tangent() = let(c1 = post_at, c2 = drum_at, r1 = post_r + cord_d / 2, r2 = drum_r + cord_d / 2,
        D = c2 - c1, L = norm(D), phi = atan2(D[1], D[0]), psi = phi - acos(-(r1 + r2) / L), n = [cos(psi), sin(psi)])
    [c1 - r1 * n, c2 + r2 * n];
function post_bottom() = [cord_x, post_at[0], post_at[1] - post_r - cord_d / 2];
function finger_path(b) = concat([post_bottom()],
    [for (k = [0:2]) for (q = guides_on(k)) at(frame(k, b), guide_at(k, q[0], -q[1]))]);
function cord_path(b) = let(t = tangent(), r = post_r + cord_d / 2, a0 = (atan2(t[0][1] - post_at[1], t[0][0] - post_at[0]) + 360) % 360)
    concat([[cord_x, t[1][0], t[1][1]]],
           [for (i = [0 : 5]) let(a = a0 + (270 - a0) * i / 6) [cord_x, post_at[0] + r * cos(a), post_at[1] + r * sin(a)]],
           finger_path(b));
// The elastic: anchor, eyelet, then in and out of each saddle's channel.
function elastic_path(b) = concat([anchor_at() + [0, 0, elastic_anchor_z() + 1], [0, 0.5, pad_top_front]],
    [for (k = [0:2]) for (y = (k == 0 ? [prox_start, E[0] - gap / 2] : k == 1 ? [gap / 2, E[1] - gap / 2] : [gap / 2, elastic_exit()]))
        at(frame(k, b), [0, y, chan_z(k, y)])],
    [at(frame(2, b), [0, elastic_exit(), top_z(2, elastic_exit())])]);
function path_len(p) = len(p) < 2 ? 0 : norm(p[1] - p[0]) + path_len([for (i = [1:len(p) - 1]) p[i]]);

module line(p, d) for (i = [0 : len(p) - 2]) hull() { translate(p[i]) sphere(d = d, $fn = 12); translate(p[i + 1]) sphere(d = d, $fn = 12); }
module hardware(b) {
    // M3x6 at the MCP, head outside the tab
    translate([plate_x, 0, 0]) rotate([0, 90, 0]) cylinder(d = 3, h = mcp_plate + lug_c + mcp_tab);
    translate([tab_x + mcp_tab, 0, 0]) rotate([0, 90, 0]) cylinder(d = 5.5, h = 1.8);
    // the PIP and DIP pins
    for (j = [1:2]) multmatrix(frame(j - 1, b)) translate([fork_in(j), E[j - 1], 0])
        rotate([0, 90, 0]) cylinder(d = 1.75, h = stack_out(j) - fork_in(j));
    // M3x20 axle, nyloc, lock pin
    translate([drum_x0() - 0.3 - cheek_t, drum_at[0], drum_at[1]]) rotate([0, 90, 0]) cylinder(d = 3, h = cheek_t + 0.3 + 2 * flange_t + drum_w + 1);
    translate([drum_x0() - 0.3 - cheek_t - 1, drum_at[0], drum_at[1] + lock_r]) rotate([0, 90, 0]) cylinder(d = 1.75, h = cheek_t + 0.3 + 2 + 1);
}

module mechanism(b, hand = false) {
    color("#9aa6b8") base();
    color("#d9dde3") for (k = [0:2]) saddle_at(k, b);
    color("#5b8def") drum2();
    color("#e0662a") line(cord_path(b), cord_d);
    color("#3a9d5a") line(elastic_path(b), elastic_d);
    color("#6b7380") hardware(b);
    if (hand) color("#e2b49a", 0.5) finger(0, b);
}

// ---------- print poses (print_gen_04.py drops each on z = 0) ----------

// Saddles print top-down: the flat top on the bed. It tapers along y, so
// first tilt it level about its proximal top edge.
module print_saddle(k) let(y0 = k == 0 ? prox_start : 0, z0 = top_z(k, y0),
        tilt = atan2(top_z(k, y0) - top_z(k, E[k]), E[k] - y0))
    rotate([180, 0, 0]) translate([0, y0, z0]) rotate([tilt, 0, 0]) translate([0, -y0, -z0]) saddle(k);
module print_part(n) {
    if (n == "proximal") print_saddle(0);
    if (n == "middle") print_saddle(1);
    if (n == "distal") print_saddle(2);
    if (n == "base") base();                // upright: supports under the pad and the post
    if (n == "drum") drum_flat();           // ulnar flange down
    if (n == "coupon") coupon();
}

// ---------- the bodies the check intersects ----------

module body(n) {
    if (n == "base") base();
    if (n == "proximal") saddle_at(0);
    if (n == "middle") saddle_at(1);
    if (n == "distal") saddle_at(2);
    if (n == "drum") drum2();
    if (n == "saddles") for (k = [0:2]) saddle_at(k);
    if (n == "printed") { base(); drum2(); for (k = [0:2]) saddle_at(k); }
    if (n == "finger") { finger(g); palm_local(g); }      // the comfort volume: his index and palm
    if (n == "middle_finger") translate(hand_mcp(1) - M) rotate([0, 0, -middle_splay]) hand_finger(1, neighbour_grow, 0, middle_flex);
    if (n == "thumb") translate(-M) hand_thumb(neighbour_grow, 0, thumb_yaw, thumb_flex);
    if (n == "cord") line(cord_path(bend), cord_d);
    if (n == "elastic") line(elastic_path(bend), elastic_d);
}

// ---------- output ----------

if (part == "print") print_part(piece);
else multmatrix(tr(M)) {
    if (part == "parts") { echo(["base"]); echo(["proximal"]); echo(["middle"]); echo(["distal"]); echo(["drum"]); }
    if (part == "assembly") mechanism(bend);
    if (part == "poses") for (i = [0:2]) translate([0, 150 * i, 0])
        mechanism([[0, 0, 0], [45, 55, 35], limit][i], true);
    if (part == "base") base();
    if (part == "proximal") saddle_at(0);
    if (part == "middle") saddle_at(1);
    if (part == "distal") saddle_at(2);
    if (part == "drum") drum2();
    if (part == "check") intersection() { body(pair[0]); body(pair[1]); }
    if (part == "path") {
        echo(cord = cord_path(bend), elastic = elastic_path(bend));
        echo(axes = [[0, 0, 0], at(frame(0), [0, E[0], 0]), at(frame(1), [0, E[1], 0])]);
        cube(0.1);
    }
}
