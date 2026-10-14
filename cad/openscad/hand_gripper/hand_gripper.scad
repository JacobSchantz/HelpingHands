// =============================================================================
//  hand_gripper.scad — a handheld gripper you wear: four fingers in one jaw,
//  thumb in the other, squeeze to close.  (voice-6d8b9fd8)
// =============================================================================
//  Topology is the SO-101's own: one FIXED jaw and one jaw that swings about a
//  single pivot.  Here the fixed jaw is the FINGER SLEEVE (your four fingers
//  lie in a contoured tunnel, palm down) and the moving jaw is the THUMB CUP
//  (your thumb sits under the fingers, like a sock puppet's mouth).  Pinching
//  thumb toward fingers swings the thumb jaw up and closes the tips; a rubber
//  band behind the pivot pulls it open again against a hard stop.
//
//  Frame (right hand, palm down):  +X along the fingers toward the jaw tips,
//  +Z up (back of the hand), +Y toward the thumb side.  x = 0 is the knuckle
//  line.  The pivot axis runs along Y, outboard of the index finger.
//
//      openscad hand_gripper.scad                       # assembly, closed
//      openscad -D 'opening=60' hand_gripper.scad       # 60 mm gape at the tips
//      openscad -D 'hand="L"' hand_gripper.scad         # S / M / L hands
//      openscad -D 'part="upper"' hand_gripper.scad     # one printable part
// =============================================================================

part    = "assembly";   // assembly | in_hand | upper | lower | pads | clash
hand    = "M";          // S | M | L — or edit the measured numbers below
handed  = "right";      // "left" mirrors everything
opening = 0;            // mm of gape between the tip pads (0 = closed)
swing   = -1;           // degrees; >= 0 overrides opening and ignores the stop (tests)

$fn = 48;

// ---------------------------------------------------------------- the hand ---
// Measure your own hand and type the numbers in; the presets just scale M.
s = hand == "S" ? 0.9 : hand == "L" ? 1.1 : 1.0;
finger_d    = [19.0, 19.5, 18.5, 16.5] * s;  // index .. pinky, across the PIP joint
finger_len  = [70,   78,   73,   58  ] * s;  // knuckle line -> fingertip
thumb_d     = 23 * s;                        // across the thumb IP joint
thumb_len   = 44 * s;                        // how much thumb goes in the cup
thumb_x     = 42 * s;                        // where the thumb tip lands, under the fingers
thumb_yaw   = 12;                            // thumb points forward and in

clear       = 1.6;   // added to every finger/thumb diameter
web         = 1.2;   // how much neighbouring finger channels overlap -> the ridges
wall        = 2.6;   // sleeve and cup wall
thumb_gap   = 4.0;   // sleeve floor to cup top when closed (nothing to pinch)

// ---------------------------------------------------------------- the jaws ---
jaw_reach   = 42;    // tips this far past the middle fingertip
jaw_w       = 20;    // jaw width across Y (SO-101 fixed jaw ~ 20)
jaw_root_h  = 14;    // blade depth where it leaves the hand
jaw_tip_h   = 7;     // blade depth at the tip
pad_len     = 26;    // TPU pad at each tip
pad_t       = 1.6;   // pad thickness = how far it stands proud of the blade
open_max_deg = 28;   // hard stop

// ---------------------------------------------------------------- hardware ---
pivot_d     = 4.4;   // M4 shoulder bolt / M4 bolt + nyloc
ear_t       = 6.0;   // each hinge ear along Y
ear_gap     = 0.4;
boss_r      = 8.0;
tail_len    = 26;    // band posts this far behind the pivot
post_d      = 6;
cam_nut_af  = 11.3;  // 1/4"-20 hex nut across flats (+clearance)
cam_nut_t   = 5.8;
cam_bolt_d  = 6.6;

// ------------------------------------------------------- derived geometry ---
function cum(i) = i == 0 ? 0 : cum(i - 1) + (finger_d[i - 1] + finger_d[i]) / 2 - web;
fy_raw = [for (i = [0 : 3]) -cum(i)];
fy     = [for (i = [0 : 3]) fy_raw[i] - (fy_raw[0] + fy_raw[3]) / 2];  // index +Y

fr     = [for (i = [0 : 3]) (finger_d[i] + clear) / 2];               // channel radii
fz     = [for (i = [0 : 3]) fr[i]];                                    // floors at z = 0
top_z  = max([for (i = [0 : 3]) fz[i] + fr[i]]) + wall;

y_pinch = (fy[0] + fy[1]) / 2;                    // thumb opposes index/middle
z_c     = -wall - thumb_gap / 2;                  // the plane the jaws close on
x_tip   = finger_len[1] + jaw_reach;

tr      = (thumb_d + clear) / 2;
t_front = [thumb_x, y_pinch + 2, -wall - thumb_gap - wall - tr];  // thumb tip centre

y_ear_u = fy[0] + fr[0] + wall + 1;               // upper ear, against the sleeve
y_ear_l = y_ear_u + ear_t + ear_gap;              // lower ear, outboard of it
P       = [-6, 0, z_c];                           // pivot (y is along the axis)
R_tip   = x_tip - P[0];
theta   = swing >= 0 ? swing : min(open_max_deg, 2 * asin(min(1, opening / (2 * R_tip))));

echo(str("tip radius ", R_tip, " mm; gape at the stop ",
         round(2 * R_tip * sin(open_max_deg / 2)), " mm; thumb travel at the stop ",
         round(2 * (t_front[0] - P[0]) * sin(open_max_deg / 2)), " mm"));

// -------------------------------------------------------------- utilities ---
module along_x(p, r, x0, x1) {                    // cylinder along X at (y,z)
    translate([x0, p[0], p[1]]) rotate([0, 90, 0]) cylinder(r = r, h = x1 - x0);
}
module along_y(p, r, y0, y1) {                    // cylinder along Y at (x,z)
    translate([p[0], y0, p[1]]) rotate([-90, 0, 0]) cylinder(r = r, h = y1 - y0);
}
module about_pivot(a) { translate(P) rotate([0, a, 0]) translate(-P) children(); }
module mirror_hand() { if (handed == "left") mirror([0, 1, 0]) children(); else children(); }

// -------------------------------------------------- upper arm: the sleeve ---
module finger_channels(extra = 0) {
    for (i = [0 : 3]) hull() {
        along_x([fy[i], fz[i]], fr[i] + extra, -30, 0.1);
        translate([finger_len[i] - fr[i] + clear, fy[i], fz[i]]) sphere(fr[i] + extra);
    }
}

module sleeve_outer() {
    hull() for (i = [0 : 3]) hull() {
        along_x([fy[i], fz[i]], fr[i] + wall, 0, 0.1);
        translate([finger_len[i] - fr[i] + clear, fy[i], fz[i]]) sphere(fr[i] + wall);
    }
}

module upper_blade() {
    x0 = finger_len[0] - 18;
    hull() {
        translate([x0, y_pinch - jaw_w / 2, z_c]) cube([1, jaw_w, jaw_root_h + 6]);
        translate([x_tip - 4, y_pinch - jaw_w / 2 + 2, z_c])
            cube([4, jaw_w - 4, jaw_tip_h]);
    }
}

// camera wedge on the back of the hand, tilted to look at the tips
cam_x  = 22;
cam_tilt = atan((top_z + 8 - z_c) / (x_tip - cam_x));
module camera_mount() {
    translate([cam_x, y_pinch, top_z - 3]) rotate([0, cam_tilt, 0])
        difference() {
            translate([-17, -17, 0]) cube([34, 34, 9]);
            translate([0, 0, -1]) cylinder(d = cam_bolt_d, h = 20);
            translate([0, 0, -1]) cylinder(d = cam_nut_af / cos(30), h = cam_nut_t + 1, $fn = 6);
            for (dx = [-12, 12]) translate([dx, 12, -1]) cylinder(d = 3.2, h = 20);  // M3 pair
        }
}

module upper_ear() {
    hull() {
        along_y([P[0], P[2]], boss_r, y_ear_u, y_ear_u + ear_t);
        translate([0, y_ear_u, z_c - 2]) cube([26, ear_t, fz[0] + 4 - z_c]);
    }
    // bridge to the sleeve wall, kept high so the thumb cup's rear clears it
    translate([0, fy[0] + fr[0], 0]) cube([26, y_ear_u - fy[0] - fr[0] + 1, fz[0] + 4]);
    // band post, behind and above the pivot
    hull() {
        along_y([P[0], P[2]], boss_r * 0.7, y_ear_u, y_ear_u + ear_t);
        along_y([P[0] - tail_len, P[2] + 12], post_d / 2 + 1, y_ear_u, y_ear_u + ear_t);
    }
    // the open stop: a pin the lower tail runs into at open_max_deg
    // the lower tail starts atan(12/tail_len) below horizontal and swings up;
    // the pin sits one (pin r + tail half-width) further round, at r = 18
    a_stop = open_max_deg - atan(12 / tail_len) + asin((3 + 4.6) / 18);
    stop = [P[0] - 18 * cos(a_stop), P[2] + 18 * sin(a_stop)];
    hull() {
        along_y(stop, 3, y_ear_u, y_ear_l + ear_t);
        along_y([P[0] - tail_len, P[2] + 12], 3, y_ear_u, y_ear_u + ear_t);
    }
}

module upper_arm() {
    difference() {
        union() {
            sleeve_outer();
            upper_blade();
            upper_ear();
            camera_mount();
        }
        finger_channels();
        along_y([P[0], P[2]], pivot_d / 2, -100, 100);      // pivot bore
        jaw_relief();
    }
}

// --------------------------------------------- lower arm: the thumb cup ---
module thumb_frame() { translate(t_front) rotate([0, 0, -thumb_yaw]) children(); }

module thumb_tube(r, back) {
    hull() {
        sphere(r);
        translate([-back, 0, 0]) rotate([0, 90, 0]) cylinder(r = r, h = 0.1);
    }
}

module lower_blade() {
    hull() {
        translate([t_front[0] - 14, y_pinch - jaw_w / 2, z_c - jaw_root_h - 6]) cube([1, jaw_w, jaw_root_h + 6]);
        translate([x_tip - 4, y_pinch - jaw_w / 2 + 2, z_c - jaw_tip_h]) cube([4, jaw_w - 4, jaw_tip_h]);
    }
}

module lower_ear() {
    cup_side_y = t_front[1] + tr + wall - 2;
    // a plate that stays outboard of the upper ear, then a web in to the cup
    // below the upper ear's reach
    hull() {
        along_y([P[0], P[2]], boss_r, y_ear_l, y_ear_l + ear_t);
        translate([12, y_ear_l, t_front[2] - 6]) cube([22, ear_t, 12]);
    }
    translate([12, cup_side_y, t_front[2] - 6]) cube([22, y_ear_l + ear_t - cup_side_y, 12]);
    // band post, behind and below the pivot
    hull() {
        along_y([P[0], P[2]], boss_r * 0.7, y_ear_l, y_ear_l + ear_t);
        along_y([P[0] - tail_len, P[2] - 12], post_d / 2 + 1, y_ear_l, y_ear_l + ear_t);
    }
}

module lower_arm() {
    difference() {
        union() {
            thumb_frame() thumb_tube(tr + wall, thumb_len);
            lower_blade();
            lower_ear();
        }
        thumb_frame() thumb_tube(tr, thumb_len + 40);
        along_y([P[0], P[2]], pivot_d / 2, -100, 100);
        jaw_relief();
    }
}

// both blades are relieved 1 mm behind the pads, so only the pads touch
module jaw_relief() {
    translate([finger_len[0] - 30, y_pinch - jaw_w, z_c - 1]) cube([x_tip - pad_len - finger_len[0] + 30, 2 * jaw_w, 2]);
    for (sz = [1, -1])  // pad pockets
        translate([x_tip - pad_len - 1, y_pinch - jaw_w / 2 + 3, sz > 0 ? z_c - 0.01 : z_c - (pad_t - 1)])
            cube([pad_len, jaw_w - 6, pad_t - 1 + 0.01]);
}

module pads() {   // print in TPU, glue into the pockets; textured face out
    for (k = [0, 1]) translate([0, k * (jaw_w), 0]) cube([pad_len - 0.4, jaw_w - 6.4, pad_t]);
}

// ---------------------------------------------------------- the ghost hand ---
module ghost_hand() {
    color([0.95, 0.75, 0.62, 0.55]) {
        for (i = [0 : 3]) hull() {
            along_x([fy[i], fz[i]], finger_d[i] / 2, -10, 0.1);
            translate([finger_len[i] - finger_d[i] / 2, fy[i], fz[i]]) sphere(finger_d[i] / 2);
        }
        hull() {                                                  // palm
            for (i = [0, 3]) translate([-10, fy[i], fz[i]]) sphere(finger_d[i] / 2);
            for (i = [0, 3]) translate([-85, fy[i] * 0.85, fz[i] - 4]) sphere(finger_d[i] / 2 + 2);
        }
        hull() {                                                  // thumb, from the heel of the palm
            thumb_frame() sphere(thumb_d / 2);
            thumb_frame() translate([-thumb_len, 0, 0]) sphere(thumb_d / 2 + 1);
            translate([-60, fy[0] - 4, fz[0] - 6]) sphere(thumb_d / 2 + 4);
        }
    }
}

// --------------------------------------------------------------- the band ---
module band() {
    color("black") hull() {
        along_y([P[0] - tail_len, P[2] + 12], post_d / 2 + 0.6, y_ear_u + ear_t / 2 - 1, y_ear_u + ear_t / 2 + 1);
        about_pivot(theta)
            along_y([P[0] - tail_len, P[2] - 12], post_d / 2 + 0.6, y_ear_l + ear_t / 2 - 1, y_ear_l + ear_t / 2 + 1);
    }
}

module assembly(ghost = false) {
    color("SteelBlue")  upper_arm();
    color("DarkOrange") about_pivot(theta) lower_arm();
    band();
    if (ghost) ghost_hand();
}

mirror_hand() {
    if (part == "assembly") assembly();
    else if (part == "in_hand") assembly(true);
    else if (part == "upper") upper_arm();
    else if (part == "lower") lower_arm();
    else if (part == "pads") pads();
    else if (part == "clash") intersection() { upper_arm(); about_pivot(theta) lower_arm(); }
}
