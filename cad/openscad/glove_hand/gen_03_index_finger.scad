// label: index finger mechanism
// gen_03 · one index finger, to show the mechanism before any more glove
// (voice-55a7493e, Jake 2026-10-17: gen_02 was too rudimentary; design ONE
// finger first and prove how it works). gen_02 stays as it was. Never edit a
// generation once a newer one exists: copy it to the next number.
//
// Original geometry from our own requirements and jake_hand.scad's numbers
// (read with jake(), never copied or changed). REFERENCES.md lists the ideas
// that came from other hands. No CAD from any of them was used.
//
// Frame: the world frame of jake_hand.scad (palm down, +y to the fingertips,
// +x toward the thumb). Inside this file everything is built about the index
// MCP axis ("local": origin on the MCP axis, x along it, y along the finger
// at 0 deg, z to the back of the hand) and placed with tr(M) at the end.
//
// How it works:
//   saddles - three PETG shells over the back and sides of the index's three
//             phalanges, open under the finger. Neighbours are pinned on BOTH
//             sides of Jake's PIP and DIP, coaxial with his own joints (tab on
//             the distal saddle inside a lug on the proximal one, 1.75 mm
//             filament pin). The ends are cut in a V below the axis: the PIP
//             V closes at 100 deg and the DIP V at 70 deg, which are the hard
//             flexion stops; the 1.2 mm dorsal gap closes at ~5 deg of
//             hyperextension, which is the extension stop.
//   base    - a PETG shell over the back of the index metacarpal, strapped to
//             the hand. The MCP is a single M3 hinge on the radial (thumb)
//             side only: nothing fits between the index and middle knuckles.
//             A rib above the tab stops MCP hyperextension; MCP flexion is
//             only limited by the spool's travel (no hard stop, see notes).
//   cord    - ONE 1 mm braided line on the radial side. Knotted in the distal
//             saddle, it runs through guides set below each joint axis
//             (cord_low), up the base's side plate and onto the spool. Every
//             crossing is below its axis, so pulling it flexes all three
//             joints; the lever arm starts at cord_low and grows as the joint
//             bends (the guides' chord moves away from the axis).
//   elastic - one 2 mm round elastic over the top: hooked on the base above
//             the MCP, through a tunnel at each end of every saddle, knotted
//             in the distal tunnel. Above every axis, so it opens the finger
//             when the cord is let out.
//   spool   - r = 9 drum on an M3 axle on the base, with a knob for the first
//             hand-turned test and four holes for a servo horn (GUESS pattern).
//
// part = assembly | poses | base | proximal | middle | distal | spool | parts
//      | check (pair = [a, b]: their intersection, for check_gen_03.py) | path
use <jake_hand.scad>

part = "assembly";
bend = [0, 0, 0];        // MCP, PIP, DIP flexion, degrees (assembly, check, path)
pair = ["base", "proximal"];
guides = true;           // false: leave the cord guides off (the cord-clearance check)
middle_splay = 0;        // the neighbours, for the check only: the photo pose is 0 and 22
thumb_yaw = 22;

/* [Fit: as gen_02] */
clearance = 1.5;         // comfort gap all round the finger and palm
tip_room = 3;

/* [Joints] */
limit = [90, 100, 70];   // MCP, PIP, DIP flexion range
vee = [0, 98, 62];       // the V cut at the PIP and DIP ends; the gap moves the real stop ~8 deg past it (check_gen_03.py)
gap = 1.2;               // dorsal gap between neighbouring saddles at 0 deg
shell = 1.6;             // PETG wall
flap_low = 0.85;         // side walls reach this share of the half-thickness below the axis
lug_r = 4;               // PIP and DIP hinge discs
lug_t = 2;               // outer lug plate
lug_c = 0.3;             // running clearance between tab and lug
pin_d = 1.9;             // 1.75 mm filament pin, ends melted into heads
mcp_r = 5.5;             // MCP hinge disc
mcp_tab = 2.4;           // the proximal saddle's MCP tab
mcp_plate = 3;           // the base's MCP side plate
mcp_bolt = 3.3;          // M3 bolt and nyloc nut
prox_start = 15;         // the proximal saddle starts past the knuckle dome

/* [Tendon] */
cord_low = [7, 6.5, 5.5];   // below the MCP, PIP, DIP axis: the lever arm at 0 deg
cord_reach = [15, 12, 8];   // guides this far either side of each joint
cord_d = 1;                 // 1 mm braided PE line
cord_hole = 1.6;
boss_d = 3.8;
boss_len = 4;

/* [Return elastic] */
elastic_hole = 2.6;         // 2 mm round elastic

/* [Base and spool] */
base_back = 50;             // the base runs this far behind the MCP axis
spool_r = 9;
spool_at = [1, -26];        // local x, y of the axle
spool_z = 25;               // local z of the boss top
strap = 20.5;               // palm strap slot length (20 mm hook-and-loop)

$fn = 32;

// ---------- the finger, from jake_hand.scad ----------

F = 0;                                   // the index
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

// Local frame of segment k at pose b: the same rotations hand_finger() makes.
function frame(k, b = bend) = k == 0 ? rx(-b[0]) : frame(k - 1, b) * tr([0, E[k - 1], 0]) * rx(-b[k]);

// Half-width and half-thickness of segment k at y, grown by `extra`.
function half(k, y, extra) = let(f = max(0, min(1, y / E[k])))
    [(W[k] + (W[k + 1] - W[k]) * f) / 2 + extra, (T[k] + (T[k + 1] - T[k]) * f) / 2 + extra];
function side(k, y, z, extra) = let(h = half(k, y, extra)) h[0] * sqrt(max(0, 1 - pow(z / h[1], 2)));
function top(k, y) = half(k, y, g + shell)[1];
function low(k) = flap_low * (T[k] + T[k + 1]) / 4;
function xi(j) = W[j] / 2 + g + 0.1;     // inner face of the hinge layer at joint j

module finger(grow, b = bend) hand_finger(F, grow, tip_room, b);
module segment(k, grow) hand_segment(E[k], W[k], T[k], W[k + 1], T[k + 1], grow);
module palm_local(grow) translate(-M) hand_palm(grow);

// In the y-z plane, extruded along x: the layer [x0, x0 + th] on side s.
module layer(s, x0, th) translate([s > 0 ? x0 : -x0 - th, 0, 0]) rotate([90, 0, 90]) linear_extrude(th) children();

// ---------- saddles ----------

// What saddle k keeps of its shell, in the y-z plane: above the axis the ends
// are square, gap/2 off the joint; below it they lean back by half of vee,
// so the two faces meet near the joint's flexion limit.
module keep2d(k) let(y0 = k == 0 ? prox_start : gap / 2, y1 = k == 2 ? E[2] + 30 : E[k] - gap / 2,
                     Z = low(k) + 2, a = k == 0 ? 0 : vee[k] / 2, d = k == 2 ? 0 : vee[k + 1] / 2)
    polygon([[y0, 40], [y0, 0], [y0 + Z * tan(a), -Z], [y1 - Z * tan(d), -Z], [y1, 0], [y1, 40]]);

// Cord guide on saddle k at y, below its joint by z: a short tube along y
// standing just outside the radial wall, its ends flared so the line can
// turn there without a sharp edge.
function guide_at(k, y, z) = [side(k, y, z, g + shell) + 1.2, y, z];
module tube(p, len = boss_len, v = [0, 1, 0]) translate(p) rotate([0, acos(v[2] / norm(v)), atan2(v[1], v[0])]) difference() {
    cylinder(d = boss_d, h = len, center = true);
    cylinder(d = cord_hole, h = len + 1, center = true);
    for (s = [-1, 1]) translate([0, 0, s * len / 2]) scale([1, 1, s]) cylinder(d1 = cord_hole + 1.4, d2 = cord_hole, h = 1, center = true);
}
function guides_on(k) = k == 0 ? [[cord_reach[0], cord_low[0]], [E[0] - cord_reach[1], cord_low[1]]]
                      : k == 1 ? [[cord_reach[1], cord_low[1]], [E[1] - cord_reach[2], cord_low[2]]]
                      : [[cord_reach[2], cord_low[2]]];   // the distal one is the anchor

// Elastic tunnels along the top midline.
function tunnels_on(k) = k == 0 ? [prox_start + 2.5, E[0] - 5] : k == 1 ? [4, E[1] - 4] : [4];
module tunnel(k, y) let(z = top(k, y)) difference() {
    translate([-2.6, y - 1.5, z - 1.4]) cube([5.2, 3, 4.6]);
    translate([0, y, z + 1.6]) rotate([90, 0, 0]) cylinder(d = elastic_hole, h = 5, center = true);
}

module saddle(k) {
    difference() {
        union() {
            intersection() {
                difference() { segment(k, g + shell); segment(k, g + 0.1); }
                rotate([90, 0, 90]) linear_extrude(120, center = true) keep2d(k);
                translate([-50, -50, -low(k)]) cube([100, 200, 100]);
            }
            for (y = tunnels_on(k)) tunnel(k, y);
            if (guides) for (q = guides_on(k)) tube(guide_at(k, q[0], -q[1]));
            // the hinge tabs at this saddle's proximal joint
            if (k == 0) layer(1, xi(0), mcp_tab) tab2d(0, mcp_r);
            if (k > 0) for (s = [-1, 1]) layer(s, xi(k), shell) tab2d(k, lug_r);
            // the outer lugs at its distal joint, and the bridge back to the wall
            if (k < 2) for (s = [-1, 1]) {
                layer(s, xi(k + 1) + shell + lug_c, lug_t) difference() {
                    hull() for (y = [E[k], E[k] - lug_r - 4]) translate([y, 0]) circle(r = lug_r);
                    translate([E[k], 0]) circle(d = pin_d);
                }
                layer(s, xi(k + 1) + shell - 1.2, 1.2 + lug_c + 0.01)
                    translate([E[k] - lug_r - 6, -lug_r]) square([3.5, 2 * lug_r]);
            }
        }
        // room for the next saddle's tab to turn in
        if (k < 2) for (s = [-1, 1]) translate([0, E[k], 0])
            layer(s, xi(k + 1) - 2, 2 + shell + lug_c) circle(r = lug_r + lug_c);
        // proximal strap: 10 mm hook-and-loop under the finger
        if (k == 0) translate([-50, 16, -low(0) + 0.8]) cube([100, 10.5, 1.8]);
        // the knot pocket behind the anchor
        if (k == 2) let(p = guide_at(2, cord_reach[2], -cord_low[2]))
            translate(p + [0, boss_len / 2 - 1.4, 0]) rotate([-90, 0, 0]) cylinder(d = 3, h = 3);
    }
}

// A hinge tab in the y-z plane: the disc round the axis plus its join into
// the saddle (trimmed to the saddle's own end faces), pin hole through.
module tab2d(j, r) difference() {
    union() {
        circle(r = r);
        intersection() {
            hull() { circle(r = r); translate([j == 0 ? prox_start + 3 : r + 2, -r]) square([0.01, 2 * r]); }
            if (j > 0) keep2d(j); else translate([0, -r]) square([prox_start + 4, 2 * r]);
        }
    }
    circle(d = j == 0 ? mcp_bolt : pin_d);
}

module saddle_at(k, b = bend) multmatrix(frame(k, b)) saddle(k);

// ---------- base ----------

plate_x = xi(0) + mcp_tab + lug_c;       // the MCP side plate's inner face
guide_x = plate_x + mcp_plate + 1.2;     // the base's cord guides stand outside it
hook_z = 20;                             // the elastic hook's foot, local z (GUESS from the knuckle top)
function drum_z() = spool_z + 0.3 + 1.5 + 2.5;
function top_guide() = [guide_x, spool_at[1] + 4, drum_z()];

module base() difference() {
    union() {
        intersection() {
            difference() { palm_local(g + shell); palm_local(g); }
            translate([-13, -base_back, 4]) cube([13 + xi(0) - 0.3, base_back + 2, 40]);
        }
        // MCP side plate: the bolt disc, back to the shell, up to the spool's height
        layer(1, plate_x, mcp_plate) difference() {
            union() {
                hull() { circle(r = mcp_r); translate([-30, -4]) square([16, drum_z() + 2.5]); }
                translate([-cord_reach[0] - 2, -cord_low[0] + 1]) square([4, 3]);   // carries the MCP guide from above
                hull() { circle(r = mcp_r); translate([0, mcp_r + 0.6]) square([9, 3.4]); }   // over the stop rib
            }
            circle(d = mcp_bolt);
        }
        // the bridge from plate to shell, behind the tab's reach
        translate([6, -30, -4]) cube([plate_x - 6 + 0.01, 30 - mcp_r - 1.5, drum_z() + 2.5]);
        // MCP hyperextension stop: the tab's top edge lands on this rib at ~4 deg
        layer(1, xi(0) + 0.3, mcp_tab + lug_c - 0.29) translate([3, mcp_r + 0.6]) square([6, 3.4]);
        if (guides) {
            tube([guide_x, -cord_reach[0], -cord_low[0]]);
            // the top guide turns the line from the side plate toward the drum
            let(t = top_guide(), a = t - [guide_x, -cord_reach[0], -cord_low[0]], c = [spool_at[0], spool_at[1], drum_z()] - t)
                tube(t, 5, a / norm(a) - c / norm(c));
        }
        // elastic hook over the knuckle
        translate([-2.5, -3, hook_z - 3]) difference() {
            cube([5, 5, 7.5]);
            translate([-1, 1.75, 5]) cube([7, 1.5, 1.6]);
        }
        // spool boss
        translate([spool_at[0], spool_at[1], 8]) cylinder(r = 6, h = spool_z - 8);
    }
    for (b = [0 : 10 : limit[0] + 10]) finger(g, [b, 0, 0]);
    palm_local(g);
    rotate([0, 90, 0]) cylinder(d = mcp_bolt, h = 60);
    translate([spool_at[0], spool_at[1], 0]) cylinder(d = 2.6, h = 60);   // M3 self-tapping axle
    // palm strap: 20 mm hook-and-loop round the hand behind the spool
    translate([-11.5, -base_back + 1.5, 0]) cube([2.2, strap, 60]);
    translate([2, -base_back + 1.5, 4]) cube([30, strap, 2.2]);
}

// ---------- spool ----------

module spool() translate([spool_at[0], spool_at[1], spool_z + 0.3]) difference() {
    union() {
        cylinder(r = spool_r + 3, h = 1.5);
        cylinder(r = spool_r, h = 6.5);
        translate([0, 0, 6.5]) cylinder(r = spool_r + 3, h = 1.5);
        // the knob: turn it by hand for the first test
        translate([0, 0, 8]) difference() {
            cylinder(r = spool_r + 3, h = 5);
            for (a = [0 : 30 : 359]) rotate([0, 0, a]) translate([spool_r + 3.6, 0, -1]) cylinder(r = 1.4, h = 7);
        }
    }
    translate([0, 0, -1]) cylinder(d = 3.4, h = 20);
    // servo horn bolt pattern: GUESS until the real horn is measured
    for (a = [45 : 90 : 359]) rotate([0, 0, a]) translate([8, 0, 8]) cylinder(d = 2.2, h = 10);
    // the line's end: through the drum, knotted inside
    translate([0, 0, 4]) rotate([0, 90, 0]) cylinder(d = cord_hole, h = spool_r + 1);
    translate([spool_r - 3, 0, 4]) rotate([0, 90, 0]) cylinder(d = 3, h = 2);
}

// ---------- the line and the elastic (drawn, not printed) ----------

// Where the line runs at pose b, spool to knot. The finger part of it is
// what changes; excursion(b) = path_len(0) - path_len(b) is how much the
// spool has to wind in. check_gen_03.py reads these from part = "path".
function finger_path(b) = concat(
    [[guide_x, -cord_reach[0], -cord_low[0]]],
    [for (k = [0:2]) for (q = guides_on(k)) at(frame(k, b), guide_at(k, q[0], -q[1]))]);
function cord_path(b) = let(t = top_guide(), d = [t[0] - spool_at[0], t[1] - spool_at[1]], n = norm(d))
    let(r = spool_r + cord_d / 2 + 0.1) concat([[spool_at[0] + r * d[0] / n, spool_at[1] + r * d[1] / n, drum_z()], t], finger_path(b));
function elastic_path(b) = concat([[0, -0.5, hook_z + 3]],
    [for (k = [0:2]) for (y = tunnels_on(k)) at(frame(k, b), [0, y, top(k, y) + 1.6])]);
function path_len(p) = len(p) < 2 ? 0 : norm(p[1] - p[0]) + path_len([for (i = [1:len(p) - 1]) p[i]]);

module line(p, d) for (i = [0 : len(p) - 2]) hull() { translate(p[i]) sphere(d = d, $fn = 12); translate(p[i + 1]) sphere(d = d, $fn = 12); }
module pins(b) {
    rotate([0, 90, 0]) translate([0, 0, xi(0) - 1]) cylinder(d = 3, h = mcp_tab + mcp_plate + 5);
    for (j = [1:2], s = [-1, 1]) multmatrix(frame(j - 1, b)) translate([s * (xi(j) + shell / 2 + lug_t / 2 + lug_c / 2), E[j - 1], 0])
        rotate([0, 90, 0]) cylinder(d = 1.75, h = shell + lug_t + lug_c + 1.6, center = true);
}

module mechanism(b, hand = false) {
    color("#9aa6b8") base();
    color("#d9dde3") for (k = [0:2]) saddle_at(k, b);
    color("#5b8def") spool();
    color("#e0662a") line(cord_path(b), cord_d);
    color("#3a9d5a") line(elastic_path(b), 2);
    color("#6b7380") pins(b);
    if (hand) color("#e2b49a", 0.5) finger(0, b);
}

// ---------- the bodies the check intersects ----------

module body(n) {
    if (n == "base") base();
    if (n == "proximal") saddle_at(0);
    if (n == "middle") saddle_at(1);
    if (n == "distal") saddle_at(2);
    if (n == "spool") spool();
    if (n == "saddles") for (k = [0:2]) saddle_at(k);
    if (n == "printed") { base(); spool(); for (k = [0:2]) saddle_at(k); }
    if (n == "finger") { finger(g); palm_local(g); }      // the comfort volume: his index and palm
    if (n == "middle_finger") translate(hand_mcp(1) - M) rotate([0, 0, -middle_splay]) hand_finger(1, g, tip_room, [0, 0, 0]);
    if (n == "thumb") translate(-M) hand_thumb(g, tip_room, thumb_yaw, [0, 0]);
    if (n == "cord") line(cord_path(bend), cord_d);
    if (n == "elastic") line(elastic_path(bend), 2);
}

// ---------- output, in the hand's frame ----------

multmatrix(tr(M)) {
    if (part == "parts") { echo(["base"]); echo(["proximal"]); echo(["middle"]); echo(["distal"]); echo(["spool"]); }
    if (part == "assembly") mechanism(bend);
    if (part == "poses") for (i = [0:2]) translate([0, 150 * i, 0])
        mechanism([[0, 0, 0], [45, 55, 35], limit][i], true);
    if (part == "base") base();
    if (part == "proximal") saddle_at(0);
    if (part == "middle") saddle_at(1);
    if (part == "distal") saddle_at(2);
    if (part == "spool") spool();
    if (part == "check") intersection() { body(pair[0]); body(pair[1]); }
    if (part == "path") {
        echo(cord = finger_path(bend), elastic = elastic_path(bend));
        echo(lengths = [path_len(finger_path(bend)), path_len(elastic_path(bend))]);
        cube(0.1);
    }
}
