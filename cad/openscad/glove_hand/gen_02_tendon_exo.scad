// label: tendon exoskeleton
// gen_02 · tendon exoskeleton (voice-55a7493e). Never edit a generation once a
// newer one exists: copy the newest gen_NN_*.scad to the next number and
// change the copy.
//
// The first robot hand: Jake's hand goes inside, the robot can wear it too.
// Designed from scratch (REFERENCES.md: which ideas came from where; no
// geometry or files were copied). Two independent inputs, as in gen_01:
//   - the hand: jake_hand.scad (correct the hand there),
//   - this file: fit, pose, and the exoskeleton's own sizes.
//
// What touches the hand:
//   pad     - one 0.8 mm TPU layer under the palm and fingers, up to pad_top.
//             The only material between his hand and an object.
//   saddles - three rigid shells per finger (two on the thumb) over the back
//             and sides of each phalanx, overlapping the pad's rim. Each pair
//             is pinned at the side of Jake's own PIP / DIP (thumb MCP / IP),
//             coaxial with his joint, so nothing rubs as he bends.
//   back    - the back-of-hand plate, the thumb's metacarpal shell, the web
//             posts, and the forearm deck with seven servo windows (the Aero
//             Hand's left-hand layout: index, middle, ring, pinky, thumb
//             flex, thumb tendon, thumb abduction).
//
// The tendon: one cord loop per digit. Both ends wind on that digit's servo
// spool; the loop runs down each side of the finger through eyelets set
// below the joint axes, and crosses over the fingertip in the tip saddle.
// Below-axis cords flex every joint; a dorsal elastic (hooks on each saddle)
// opens it again, the same cord + return spring the Aero Hand uses, so
// transparent teaching works unchanged. The MCP has no hardware: no rigid
// part can sit beside a middle or ring knuckle, so the cords cross it low
// in the finger webs, through the web posts. That needs the fingers spread
// (splay below); the posts fill the gaps between them.
//
// part = assembly | curl (fingers bent, cords drawn) | pad | saddles | back
//      | comfort | hand | parts
use <jake_hand.scad>

part = "assembly";

/* [Fit: as gen_01] */
clearance_palm = 2.0;
clearance_fingers = 1.5;
clearance_thumb = 2.0;
tip_room = 3;
pad = 0.8;             // TPU 95A, palm side
pad_top = 6;           // the pad's rim, mm above the palm surface
wrist_cut = 5;

/* [Pose, degrees] */
splay = [22, 4, -14, -32];  // 18 deg between fingers, wider than gen_01: room for the web posts and hinge lugs
thumb_yaw = 40;             // further out than gen_01, so the thumb saddles clear the palm
curl = [[45, 60, 40], [45, 60, 40], [45, 60, 40], [45, 60, 40], [0, 30, 30]];  // part="curl" only

/* [Exoskeleton] */
shell = 1.6;           // saddle and back plate wall, PETG
lug_r = 4;             // hinge lug radius around the joint axis
lug_t = 2;             // outer lug thickness (the inner lug is the saddle wall)
pin_d = 1.9;           // a 1.75 mm filament pin, heads melted over
joint_gap = 1.2;       // between neighbouring saddles, beyond the lugs
flap_low = 0.85;       // side flaps reach this fraction of the half-thickness below the axis
cord_low = 0.7;        // eyelet height below the axis, same units: the cord's lever arm
cord_hole = 1.5;       // 1 mm braided line
web = 18;              // web post, mm past the knuckle along the finger
post = [2.4, 5];       // web post section: across, along
band_start = 15;       // the proximal saddle starts this far past the knuckle, top only...
flap_start = 28;       // ...and gets its side flaps (and first eyelets) past the web post
plate_front = 81;      // back plate front edge (y), behind the pinky's knuckle

/* [Servo deck: STS3215 envelope, GUESS from ../hand_gripper] */
servo = [24.7, 45.2, 35];   // across, along, tall; shaft up, 11 mm from the hand end
servo_gap = 2;
deck_y = -22;               // the deck's hand-side edge
deck_t = 4;
deck_lift = 6;              // above the top of the wrist

$fn = 28;

// ---------- the hand and its frames ----------

g_in_f = clearance_fingers + pad;   // saddles sit on the pad's outside
g_in_p = clearance_palm + pad;
g_in_t = clearance_thumb + pad;

module hand(g = 0, flex = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]], thumb_flex = [0, 0])
    jake_hand(grow = g, tip_room = tip_room, splay = splay, flex = flex, thumb_yaw = thumb_yaw, thumb_flex = thumb_flex);
module comfort() hand([clearance_palm, clearance_fingers, clearance_thumb]);

function lerp4(a, b) = [for (k = [0:3]) a + (b - a) * k / 3];
function tr(v) = [[1, 0, 0, v[0]], [0, 1, 0, v[1]], [0, 0, 1, v[2]], [0, 0, 0, 1]];
function rx(a) = [[1, 0, 0, 0], [0, cos(a), -sin(a), 0], [0, sin(a), cos(a), 0], [0, 0, 0, 1]];
function rz(a) = [[cos(a), -sin(a), 0, 0], [sin(a), cos(a), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
function apply(m, p) = let(q = m * [p[0], p[1], p[2], 1]) [q[0], q[1], q[2]];

// Digit d = 0..3 index..pinky, 4 thumb: [base frame, segment lengths, widths, thicknesses, grow].
// Segment k runs along +y of its own frame from its joint; z = 0 is the joint axis.
function digit(d) = d < 4
    ? let(L = jake("finger_len")[d] * jake("phalanx"),
          w = lerp4(jake("finger_base_w")[d], jake("finger_tip_w")[d]),
          t = lerp4(jake("finger_base_t")[d], jake("finger_tip_t")[d]))
      [tr(hand_mcp(d)) * rz(-splay[d]), [L[0], L[1], L[2] - min(w[3], t[3]) / 2 + tip_room], w, t, g_in_f]
    : let(L = jake("thumb_len"), w = jake("thumb_w"), t = jake("thumb_t"), c = jake("thumb_cmc"))
      [tr([c[0], c[1], t[0] / 2]) * rz(-thumb_yaw), [L[0], L[1], L[2] - min(w[3], t[3]) / 2 + tip_room], w, t, g_in_t];

// World frame of segment k of digit d, bent by flex = [k0, k1, k2] (the thumb's k0 is its fixed CMC).
function seg_frame(d, k, flex) = let(D = digit(d))
    k == 0 ? D[0] * rx(-flex[0]) : seg_frame(d, k - 1, flex) * tr([0, D[1][k - 1], 0]) * rx(-flex[k]);

// Half-width, half-thickness and side-surface x at height z of segment k at y (grow g).
function seg_wt(d, k, y) = let(D = digit(d), f = max(0, min(1, y / D[1][k])))
    [D[2][k] + (D[2][k + 1] - D[2][k]) * f, D[3][k] + (D[3][k + 1] - D[3][k]) * f];
function side_x(d, k, y, z, g) = let(wt = seg_wt(d, k, y), a = wt[0] / 2 + g, b = wt[1] / 2 + g)
    a * sqrt(max(0, 1 - pow(z / b, 2)));
function cord_z(d, k, y) = -cord_low * seg_wt(d, k, y)[1] / 2;

module segment(d, k, g) let(D = digit(d))
    hand_segment(D[1][k], D[2][k], D[3][k], D[2][k + 1], D[3][k + 1], g);

// ---------- saddles ----------

// Where along segment k the saddle body runs, and the cord eyelets on it.
function body_y(d, k) = let(e = digit(d)[1][k], first = d < 4 ? band_start : lug_r + joint_gap)
    [k == 0 ? first : lug_r + joint_gap, k == 2 ? e + 30 : e - lug_r - joint_gap];
function eyelets(d, k) = let(y = body_y(d, k), e = digit(d)[1][k])
    k == 0 && d < 4 ? [flap_start + 2, y[1] - 2]
    : k == 2 ? [y[0] + 2, e - 6] : [y[0] + 2, y[1] - 2];

module eyelet(d, k, y, s) let(g = digit(d)[4] + shell, z = cord_z(d, k, y), x = side_x(d, k, y, z, g) + 1)
    translate([s * x, y, z]) rotate([-90, 0, 0]) difference() {
        cylinder(d = cord_hole + 2.4, h = 3, center = true);
        cylinder(d = cord_hole, h = 4, center = true);
    }

module saddle_body(d, k) let(D = digit(d), g = D[4], y = body_y(d, k), t = D[3][k])
    intersection() {
        difference() { segment(d, k, g + shell); segment(d, k, g); }
        union() {
            // top-only band through the web, then full side flaps
            from = k == 0 && d < 4 ? flap_start : y[0];
            translate([-50, y[0], 0.7 * t / 2]) cube([100, from - y[0] + 0.01, 50]);
            translate([-50, from, -flap_low * t / 2]) cube([100, y[1] - from, 60]);
        }
    }

// The lug plate on one side of joint j (between segment j - 1 and j), in the
// frame where that joint is at y = 0: outer = on the proximal saddle.
module lug(d, j, s, outer) let(g = digit(d)[4], hw = digit(d)[2][j] / 2, back = outer ? -1 : 1)
    difference() {
        hull() for (y = [0, back * (lug_r + joint_gap + 2)])
            translate([s * (hw + g + (outer ? shell : 0)) + (s < 0 ? -(outer ? lug_t : shell) : 0), y, 0])
                rotate([0, 90, 0]) cylinder(r = lug_r, h = outer ? lug_t : shell);
        rotate([0, 90, 0]) cylinder(d = pin_d, h = 100, center = true);
    }

// Saddle k of digit d, in its own segment frame.
module saddle(d, k) let(e = digit(d)[1][k]) {
    saddle_body(d, k);
    for (s = [-1, 1]) {
        for (y = eyelets(d, k)) eyelet(d, k, y, s);
        if (k < 2) translate([0, e, 0]) lug(d, k + 1, s, true);
        if (k > 0) lug(d, k, s, false);
    }
    // the cord crosses over the fingertip here, and a hook for the return elastic on top
    if (k == 2) translate([0, e - 6, seg_wt(d, k, e - 6)[1] / 2 + digit(d)[4] + shell])
        rotate([0, 90, 0]) difference() { cylinder(d = cord_hole + 2.4, h = seg_wt(d, k, e)[0], center = true);
                                           cylinder(d = cord_hole, h = 100, center = true); }
    hook_y = k == 0 && d < 4 ? flap_start : body_y(d, k)[0] + 3;
    translate([0, hook_y, seg_wt(d, k, hook_y)[1] / 2 + digit(d)[4] + shell - 0.5]) elastic_hook();
}

module elastic_hook() difference() {
    translate([-2, -2, 0]) cube([4, 4, 3.5]);
    translate([-3, -0.75, 1.2]) cube([6, 1.5, 1.4]);
}

module saddles(flex = [for (d = [0:4]) [0, 0, 0]])
    for (d = [0:4]) for (k = [d < 4 ? 0 : 1:2]) multmatrix(seg_frame(d, k, flex[d])) saddle(d, k);

// ---------- back: plate, thumb metacarpal, web posts, deck ----------

function knuckle_top() = jake("palm_thick") + g_in_p + shell;
function wrist_top() = jake("wrist_thick") + g_in_p + shell;
function deck_z() = wrist_top() + deck_lift;
function servo_xy(n) = let(p = servo[0] + servo_gap, row = n < 4 ? 0 : 1, i = n < 4 ? n : n - 4)
    [p * ((row == 0 ? 1.5 : 1) - i), deck_y - 11 - row * (servo[1] + servo_gap)];
deck_len = 2 * (servo[1] + servo_gap) + 6;
deck_w = 4 * (servo[0] + servo_gap) + 6;

// Web post p sits on the far side of finger p - 1 and the near side of finger p:
// p = 0 is outside the index, 4 outside the pinky.
function web_point(d, s) = apply(digit(d)[0], [s * (side_x(d, 0, web, 0, g_in_f) + post[0] / 2 + 0.6), web, 0]);
function post_xy(p) = let(a = p > 0 ? web_point(p - 1, -1) : undef, b = p < 4 ? web_point(p, 1) : undef)
    p == 0 ? b : p == 4 ? a : (a + b) / 2;
function post_angle(p) = -(p == 0 ? splay[0] : p == 4 ? splay[3] : (splay[p - 1] + splay[p]) / 2);
function post_hole_z(p) = let(d = p == 4 ? 3 : p) jake("finger_base_t")[d] / 2 + cord_z(d, 0, web);

module web_post(p) let(c = post_xy(p), top = knuckle_top() + 1) {
    difference() {
        translate([c[0], c[1], 0]) rotate([0, 0, post_angle(p)]) translate([-post[0] / 2, -post[1] / 2, 1])
            cube([post[0], post[1], top - 1]);
        translate([c[0], c[1], post_hole_z(p)]) rotate([0, 0, post_angle(p)])
            rotate([90, 0, 0]) cylinder(d = cord_hole, h = 20, center = true);
    }
    // the arm back over the knuckles to the plate
    hull() {
        translate([c[0], c[1], top - 2]) rotate([0, 0, post_angle(p)]) translate([-post[0] / 2, -post[1] / 2, 0])
            cube([post[0], post[1], 2]);
        translate([c[0] * 0.92 - post[0] / 2, plate_front - 6, knuckle_top() + 0.5]) cube([post[0], 6, 2.5]);
    }
}

module forearm(g, len) translate([0, deck_y - deck_len, jake("wrist_thick") / 2]) rotate([-90, 0, 0])
    scale([jake("wrist_width") / 2 + g, jake("wrist_thick") / 2 + g, 1]) cylinder(r = 1, h = len, $fn = 48);

module back_plate()
    difference() {
        union() {
            intersection() {
                union() { hand_palm(g_in_p + shell); forearm(g_in_p + shell, deck_len - deck_y + 6); }
                translate([-100, deck_y - deck_len, pad_top - 2]) cube([200, plate_front - deck_y + deck_len, 100]);
            }
            // the thumb's metacarpal shell: the CMC is locked at thumb_yaw in this generation
            multmatrix(seg_frame(4, 0, [0, 0, 0])) {
                intersection() {
                    segment(4, 0, g_in_t + shell);
                    translate([-50, 0, -flap_low * digit(4)[3][1] / 2]) cube([100, digit(4)[1][0] - lug_r - joint_gap, 60]);
                }
                for (s = [-1, 1]) {
                    for (y = [digit(4)[1][0] - lug_r - joint_gap - 2]) eyelet(4, 0, y, s);
                    translate([0, digit(4)[1][0], 0]) lug(4, 1, s, true);
                }
            }
            // combs: notched ribs that hold each cord's line across the plate
            for (y = [plate_front - 22, 8]) intersection() {
                difference() {
                    hand_palm(g_in_p + shell + 4);
                    for (n = [0:6]) let(x = cord_x(n, y)) translate([x - 0.8, y - 5, 0]) cube([1.6, 10, 100]);
                }
                translate([-100, y - 2, pad_top]) cube([200, 4, 100]);
            }
        }
        hand_palm(g_in_p);
        forearm(g_in_p, deck_len - deck_y + 6);
        hand([g_in_p, g_in_f + shell + 0.4, g_in_t + 0.4]);   // keep off the fingers and thumb
        translate([-100, -wrist_cut - 200 + 0.01, -50]) cube([200, 200, pad_top + 48]);   // nothing under the forearm
    }

// Each cord's line over the plate: from its post (or the thumb) to its servo.
function cord_start(n) = n < 4 ? [post_xy(n)[0] * 0.92 + (n == 0 ? 2 : 0), plate_front]
                        : [jake("thumb_cmc")[0] - 4 - 4 * (n - 4), 52];
function cord_x(n, y) = let(a = cord_start(n), b = servo_xy(n), f = (a[1] - y) / (a[1] - b[1])) a[0] + (b[0] - a[0]) * f;

module deck()
    difference() {
        union() {
            translate([-deck_w / 2, deck_y - deck_len, deck_z()]) cube([deck_w, deck_len, deck_t]);
            for (x = [-1, 1]) intersection() {
                translate([x * 18 - 2, deck_y - deck_len, 0]) cube([4, deck_len, deck_z() + 1]);
                forearm(g_in_p + shell + 30, deck_len);
            }
        }
        forearm(g_in_p + shell - 0.2, deck_len + 1);
        for (n = [0:6]) let(c = servo_xy(n))
            translate([c[0] - servo[0] / 2 - 0.3, c[1] - servo[1] + 11 - 0.3, deck_z() - 1]) cube([servo[0] + 0.6, servo[1] + 0.6, deck_t + 2]);
    }

module back() { back_plate(); for (p = [0:4]) web_post(p); deck(); }

// ---------- pad ----------

module pad_piece()
    difference() {
        intersection() {
            difference() { hand([g_in_p, g_in_f, g_in_t]); comfort(); }
            translate([-200, -wrist_cut, -50]) cube([400, 400, 50 + pad_top]);
        }
    }

// ---------- cords (drawn, not printed) ----------

module cord(points) for (i = [0:len(points) - 2]) hull() { translate(points[i]) sphere(d = 1); translate(points[i + 1]) sphere(d = 1); }

function eyelet_world(d, k, y, s, flex) = let(g = digit(d)[4] + shell, z = cord_z(d, k, y))
    apply(seg_frame(d, k, flex), [s * (side_x(d, k, y, z, g) + 1), y, z]);

module cords(flex) {
    spool = function(n) let(c = servo_xy(n)) [c[0], c[1], deck_z() + servo[2] - 4];
    for (d = [0:4]) for (s = [-1, 1]) {
        f = flex[d];
        e = digit(d)[1];
        tip = apply(seg_frame(d, 2, f), [s * seg_wt(d, 2, e[2] - 6)[0] / 2, e[2] - 6, seg_wt(d, 2, e[2] - 6)[1] / 2 + digit(d)[4] + shell]);
        on = [for (k = [2:-1:d < 4 ? 0 : 1]) for (y = [eyelets(d, k)[1], eyelets(d, k)[0]]) eyelet_world(d, k, y, s, f)];
        p = d < 4 ? (s > 0 ? d : d + 1) : -1;
        n = d;
        route = d < 4
            ? [[post_xy(p)[0], post_xy(p)[1], post_hole_z(p)],
               [post_xy(p)[0], post_xy(p)[1], knuckle_top() + 1],
               [cord_start(n)[0], plate_front - 6, knuckle_top() + 2]]
            : [eyelet_world(4, 0, digit(4)[1][0] - lug_r - joint_gap - 2, s, [0, 0, 0]),
               [cord_start(n)[0], cord_start(n)[1], knuckle_top() + 2]];
        cord(concat([tip], on, route,
                    [[cord_x(n, plate_front - 22), plate_front - 22, knuckle_top() + 3],
                     [cord_x(n, 8), 8, wrist_top() + 3], spool(n)]));
    }
}

// ---------- parts ----------

if (part == "parts") { echo(["pad"]); echo(["saddles"]); echo(["back"]); }
if (part == "assembly") {
    color("#2b2f36") pad_piece();
    color("#d9dde3") saddles();
    color("#9aa6b8") back();
    color("#e0662a") cords([for (d = [0:4]) [0, 0, 0]]);
    color("#444a", 0.35) for (n = [0:6]) let(c = servo_xy(n)) translate([c[0] - servo[0] / 2, c[1] - servo[1] + 11, deck_z() + deck_t - 8]) cube(servo);
}
if (part == "curl") {
    color("#e2b49a") hand(0, [for (d = [0:3]) curl[d]], [curl[4][1], curl[4][2]]);
    color("#d9dde3") saddles(curl);
    color("#9aa6b8") back();
    color("#e0662a") cords(curl);
}
if (part == "pad") pad_piece();
if (part == "saddles") saddles();
if (part == "back") back();
if (part == "comfort") comfort();
if (part == "hand") hand();
