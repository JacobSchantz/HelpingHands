# Robot Glove Hand · references

Jake's rule (voice-55a7493e, 2026-10-17): **design from scratch.** No geometry,
files, or code from any of these went into this folder. They were studied for
ideas only (tendon routing, pulley sizing, printable joints and tolerances).
Each entry says which idea came from it and where that idea shows up here.
Licences are listed so a future generation knows what borrowing *would* need.
"Unverified" means it was not checked from the repo itself in this pass.

| Project | Where | Licence | Idea taken (gen_02) |
|---|---|---|---|
| Aero Hand Open (TetherIA / Chestnut Robotics), our current hand | https://github.com/chestnut-robotics/aero-hand-open (vendored firmware/SDK in `third_party/aero_hand/upstream`) | Apache-2.0 (verified, `upstream/LICENSE.md`) | One flexion cord per finger on a servo spool plus a return spring. Seven actuators in this order: thumb abd / flex / tendon, index, middle, ring, pinky. The left-hand layout. Torque-mode "transparent" teaching, which is why gen_02 keeps cord + spring. |
| LEAP Hand (CMU) | https://leaphand.com · https://github.com/leap-hand | unverified | Contrast only: it is direct-drive, with servos in the joints. That is the reason to keep motors *off* the fingers, so the inside stays clear for a human hand. |
| ORCA Hand (ETH Zurich) | https://www.orcahand.com | unverified | Tendon hand with the motors in the forearm and cords routed through the palm and wrist. Idea: put the servo deck behind the wrist, not on the fingers. |
| Amazing Hand (Pollen Robotics) | https://github.com/pollen-robotics/AmazingHand | unverified | Small servos per finger and a cheap printed build. Idea: aim for parts that print without supports on a hobby printer. |
| InMoov (Gaël Langevin) | https://inmoov.fr | CC BY-NC (unverified) | Braided-line tendons from forearm servos, with a pull loop for each finger. Idea: one *loop* per finger (both ends on one spool), so the two sides share tension. |
| DexHand | https://www.dexhand.org | unverified | Tendons through printed eyelets on each phalanx. Idea: eyelets as small printed rings on the side of each segment. |
| Open Bionics (Ada hand; the Hero Arm is not open) | https://openbionics.com · https://github.com/Open-Bionics | Ada: CC BY-SA (unverified) | Wearable proportions and tendon return by elastic. Idea: the dorsal elastic hook on every saddle. |
| Soft exo-gloves: Exo-Glove (SNU), Harvard soft robotic glove | papers (In et al. 2015; Polygerinos et al. 2015) | papers | Tendon exo-gloves route flexion cords under the palm. That is exactly what Jake ruled out, which showed the constraint: from the back you can't flex a knuckle with a cord unless it passes below the axis. Hence side eyelets below the axes, and web posts for the MCP. |

Everything else in gen_02 is designed here: the saddle/pad split, side pins
coaxial with Jake's PIP/DIP, the web posts, the combs, and the deck.
