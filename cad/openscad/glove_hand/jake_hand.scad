// Jake's LEFT hand as a 3D model, and only that (voice-0c526dc0). The glove
// files take it as input with `use <jake_hand.scad>` plus their own fit
// parameters (clearance per region, wall), so correcting the hand never means
// editing a glove, and loosening a glove never means editing the hand.
//
// Frame: palm down on the bench. z = 0 is the palm surface, +z the back of the
// hand, +y toward the fingertips, y = 0 the wrist crease, thumb toward +x.
// Every segment is a hull of two ellipsoids, so jake_hand(grow = g) is the
// hand swollen by about g mm all round: that is how a glove makes its
// comfort volume (grow = clearance) and its outer skin (clearance + wall).
//
// Where the numbers come from (README, "Measurements"):
//   top-down, tape:  ../../glove_hand/refs/jake_left_hand_fingers_together_top.jpg
//                    ../../glove_hand/refs/jake_left_hand_spread_top.jpg
//   calipers:        ../../glove_hand/refs/measurements.md
//   GUESS:           every thickness (z) below, until the side photo arrives.
// fit_check.py overlays this model's top view on the fingers-together trace.

/* [Palm] */
hand_palm_length = 98;    // wrist crease -> middle-finger knuckle (MCP). Photo: palm + middle = 193
hand_palm_width = 80;     // across the four knuckles, index edge to pinky edge. Photo: 80
hand_wrist_width = 60;    // at the wrist crease. Photo: 60
hand_palm_thick = 28;     // GUESS: palm surface to back of hand at the knuckles
hand_wrist_thick = 38;    // GUESS: at the wrist crease
hand_heel = [6, 42, 30];  // pinky-side palm bulge (hypothenar): out past the pinky knuckle, y, size

/* [Fingers: index, middle, ring, pinky] */
hand_finger_len = [88, 95, 89, 72];             // knuckle (MCP) -> tip. Photo: web-to-tip + 14
hand_finger_base_w = [20.5, 20.5, 19.5, 17.5];  // width at the knuckle; they sum to ~ the palm width
hand_finger_tip_w = [16.5, 17, 16, 14.5];       // across the last joint. Photo: 3 fingers = 50 mm
hand_finger_base_t = [20, 20.5, 19, 17];        // GUESS: thickness at the knuckle
hand_finger_tip_t = [14, 14.5, 13.5, 12.5];     // GUESS: thickness at the last joint
hand_knuckle_drop = [3, 0, 3, 13];              // knuckle row arch: how far each MCP sits below the middle's
hand_phalanx = [0.47, 0.29, 0.24];              // proximal / middle / distal share of the finger length

/* [Thumb] */
hand_thumb_cmc = [30, 22];          // base joint (CMC), x and y from the wrist-crease centre
hand_thumb_len = [44, 33, 29];      // metacarpal, proximal phalanx, distal phalanx (to the tip)
hand_thumb_w = [33, 30, 23, 19];    // width at CMC, MCP, IP, tip. Calipers: 30 at the MCP
hand_thumb_t = [26, 22, 18, 14];    // GUESS: thickness at the same four points

/* [Default pose, degrees: the fingers-together photo is all zero. A glove passes its own.] */
hand_splay = [0, 0, 0, 0];          // finger yaw, + toward the thumb
hand_flex = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]];   // [MCP, PIP, DIP] curl toward the palm, per finger
hand_thumb_yaw = 22;                // thumb metacarpal angle from +y toward +x (spread photo: ~70)
hand_thumb_flex = [0, 0];           // MCP, IP curl

$fn = 28;

// One ellipsoid: width w (x), thickness t (z), length l (y), centred at the origin.
module hand_blob(w, t, l, grow) scale([w / 2 + grow, l / 2 + grow, t / 2 + grow]) sphere(1);

// A tapered segment along +y, from (w0, t0) at the joint to (w1, t1) at length len.
// The centreline sits at half the segment's thickness so the palm side lies flat.
module hand_segment(len, w0, t0, w1, t1, grow)
    hull() {
        hand_blob(w0, t0, min(w0, t0), grow);
        translate([0, len, 0]) hand_blob(w1, t1, min(w1, t1), grow);
    }

// Finger i, built joint by joint so each flex angle bends everything after it.
module hand_finger(i, grow, tip_room, flex) {
    L = hand_finger_len[i] * hand_phalanx;
    w = [for (k = [0:3]) hand_finger_base_w[i] + (hand_finger_tip_w[i] - hand_finger_base_w[i]) * k / 3];
    t = [for (k = [0:3]) hand_finger_base_t[i] + (hand_finger_tip_t[i] - hand_finger_base_t[i]) * k / 3];
    // the tip blob's radius already reaches past the joint: pull the last centre in by it
    ends = [L[0], L[1], L[2] - min(w[3], t[3]) / 2 + tip_room];
    module chain(k)
        rotate([-flex[k], 0, 0]) {
            hand_segment(ends[k], w[k], t[k], w[k + 1], t[k + 1], grow);
            if (k < 2) translate([0, ends[k], 0]) chain(k + 1);
        }
    chain(0);
}

// x of each knuckle, packing the fingers side by side from the index edge.
function hand_mcp_x(i) = hand_palm_width / 2 - hand_widths_to(i - 1) - hand_finger_base_w[i] / 2;
function hand_widths_to(i) = i < 0 ? 0 : hand_finger_base_w[i] + hand_widths_to(i - 1);
function hand_mcp(i) = [hand_mcp_x(i), hand_palm_length - hand_knuckle_drop[i], hand_finger_base_t[i] / 2];

module hand_palm(grow) {
    hull() {
        translate([0, 0, hand_wrist_thick / 2]) hand_blob(hand_wrist_width, hand_wrist_thick, 20, grow);
        translate([-hand_palm_width / 2 - hand_heel[0] + hand_heel[2] / 2, hand_heel[1], hand_palm_thick / 2])
            hand_blob(hand_heel[2], hand_palm_thick, hand_heel[2] * 1.6, grow);
        for (i = [0:3]) translate(hand_mcp(i))
            translate([0, 0, (hand_palm_thick - hand_finger_base_t[i]) / 2])
                hand_blob(hand_finger_base_w[i], hand_palm_thick, hand_finger_base_w[i], grow);
    }
}

module hand_thumb(grow, tip_room, yaw, flex) {
    w = hand_thumb_w; t = hand_thumb_t; L = hand_thumb_len;
    ends = [L[0], L[1], L[2] - min(w[3], t[3]) / 2 + tip_room];
    translate([hand_thumb_cmc[0], hand_thumb_cmc[1], t[0] / 2])
        rotate([0, 0, -yaw]) {
            hand_segment(ends[0], w[0], t[0], w[1], t[1], grow);
            // the thenar pad: the metacarpal blended into the palm
            hull() { hand_blob(w[0], t[0], w[0], grow); translate([-18, 0, 0]) hand_blob(w[0], t[0], w[0], grow); }
            translate([0, ends[0], 0]) rotate([-flex[0], 0, 0]) {
                hand_segment(ends[1], w[1], t[1], w[2], t[2], grow);
                translate([0, ends[1], 0]) rotate([-flex[1], 0, 0])
                    hand_segment(ends[2], w[2], t[2], w[3], t[3], grow);
            }
        }
}

// The whole hand. grow = [palm, fingers, thumb] in mm, or one number for all;
// tip_room lengthens every finger and the thumb by that much past the tip.
// The pose arguments default to the photo pose above.
module jake_hand(grow = 0, tip_room = 0, splay = hand_splay, flex = hand_flex,
                 thumb_yaw = hand_thumb_yaw, thumb_flex = hand_thumb_flex) {
    g = is_list(grow) ? grow : [grow, grow, grow];
    hand_palm(g[0]);
    for (i = [0:3]) translate(hand_mcp(i)) rotate([0, 0, -splay[i]]) hand_finger(i, g[1], tip_room, flex[i]);
    hand_thumb(g[2], tip_room, thumb_yaw, thumb_flex);
    // the forearm stub, so the wrist end of anything built on the hand stays open
    translate([0, -40, hand_wrist_thick / 2]) rotate([-90, 0, 0])
        scale([hand_wrist_width / 2 + g[0], hand_wrist_thick / 2 + g[0], 1]) cylinder(r = 1, h = 40);
}

jake_hand();
