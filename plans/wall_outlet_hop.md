# Outlet Hop — unplug, drive, replug

Status: PLAN + SIMULATION. No hardware is built or bought. What is proven so far
is software only (see "Evidence" at the end). Pebble: voice-f43bda60.

## The milestone

The robot is charging from an ordinary wall outlet. It pulls its own plug, stays
powered on battery with no reboot of the Mac, iPad, controllers or radio, puts its
cord away, drives somewhere else, finds another ordinary outlet, plugs in, proves
it is charging, and keeps working. A proprietary dock does not count.

Solar, outdoor autonomy and Starlink are later. Starlink is optional until Jake
confirms it; it is just another load in the power budget.

## Three things deleted

**1. No retractable cord for this milestone.** The robot drives right up to the
outlet and charges parked. So the cord only has to span the robot itself: a short
certified pigtail, about a metre, that lives fully inside the body when stowed.
A retractable reel only earns its place when the robot must work while tethered,
and it brings a spring that tugs the plug out of the wall, a ratchet that can
jam, and a long cord to snag. Compared:

| | short captured pigtail (chosen) | spring retractable reel | motorized reel |
|---|---|---|---|
| parts | cord + clamp + channel | commercial reel | reel, motor, slip ring |
| pulls on the plug | no | yes, constantly | controllable |
| snag risk while driving | none, stowed inside | cord on the floor | cord on the floor |
| works while charging | parked only | within cord radius | within cord radius |
| revisit | — | if parked charging is too limiting | if the reel is needed and the spring fights us |

**2. The arm does not plug in.** The SO-101's STS3215 servos stall at 30 kg·cm
(about 2.9 N·m) at 12 V. At 25 cm of reach that is roughly 12 N at the gripper,
at stall. UL 498 puts plug withdrawal force between 3 and 15 lbf (13 to 67 N), and
insertion is in the same range. The arm would be at stall doing it. So the plug
rides on a small **plug carriage** on the front of the base, and the **base's
wheels supply the push and the pull.** The arm stays free for its real jobs.

**3. Nothing switches over at unplug.** In an "online" power path the wall only
feeds the battery charger. Every load always runs from the battery, whether
plugged in or not. Pulling the plug just stops the charge current. No relay
moves, so there is no transfer gap to survive. The Mac mini M4 has an internal
AC supply, so it runs from a pure sine inverter on the battery.

## Architecture

```
wall outlet ──(1 m certified pigtail)── plug carriage
                                           │
                                     AC battery charger ──► LiFePO4 battery ──► shunt
                                                                 │
                              ┌──────────────┬───────────────────┼──────────────┐
                        pure sine inverter  12 V DC-DC       base motor drive   (Starlink later)
                              │                │
                     Mac mini + iPad charger  SO-101 + controllers
```

The Mac mini runs the outlet-hop controller (`sim/outlet_hop/outlet_hop.py`). It
reads battery state of charge and current from the shunt, charger status, the
carriage's force sensor, face switch and cable-stow switch, and the camera.

## The plug carriage

- **Holder:** clamps the plug body, never the cord, so all push and pull goes
  through the plug. A clamp just behind it takes strain off the cord.
- **Height:** one lead-screw lift sets outlet height. Measure the house's outlets
  first; do not assume a height.
- **Roll:** one servo turns the plug 0, 90 or 180 degrees for ground-up,
  ground-down and sideways outlets.
- **Compliance:** the holder floats on springs a few millimetres side to side and
  up and down, with a chamfered shroud that slides on the cover plate. This absorbs
  the aim error the camera and wheels leave.
- **Force:** a load cell behind the holder. Insertion stops at 60 N and
  withdrawal at 70 N (tunable in `Limits`). If a pull exceeds the limit, it
  pushes back in, stays charging, and asks for help.
- **Seated:** a face switch closes when the holder is flush against the cover
  plate, plus travel depth. Seated alone is not "charging" (below).
- **Aim:** a front camera finds the outlet face. On the fixture it uses a printed
  fiducial first; a learned outlet detector comes after that works.

Stability is not a worry at these forces. 70 N at outlet height against a low,
battery-heavy base is small, but check it once the base is chosen.

## Cable

Stowed means the pigtail loop sits in its channel and a switch sees it. The
controller refuses to drive if mains is present or the cable is not stowed. A
stow failure gets one retry, then the robot stops where it is rather than drive
with a loose cord.

## Power path candidates

Choose by the Stage 0 test, not by spec sheets.

- **Online (preferred):** 12.8 V 100 Ah LiFePO4 (1.28 kWh); a certified plug-in
  AC charger whose own cord becomes the pigtail (Victron Blue Smart IP22 12/15 is
  a candidate); a pure sine inverter sized for the Mac and iPad (Victron Phoenix
  12/500 class); a battery shunt with Bluetooth or serial output (Victron
  SmartShunt class). Victron figures still need checking against datasheets.
- **Power station (quicker to try):** EcoFlow River 3 Plus, 286 Wh LiFePO4, with a
  claimed UPS switchover under 10 ms (the base River 3 claims under 20 ms). That is
  a switchover, so the Mac has to ride through it. Stage 0 measures whether it
  does.

Everything is plug-and-socket or low-voltage DC. No mains wiring is opened or
improvised.

## Runtime budget

| load | watts | source |
|---|---|---|
| Mac mini M4 | 4 idle, 65 max | Apple spec; measured 3–4 idle, 58–62 stress |
| iPad | ~10 | estimate |
| inverter overhead | ~5–10 | estimate, check datasheet |
| base, driving | ~40–100 | estimate until the base is chosen |
| SO-101, holding | small | estimate |

Worst plausible average, about 150 W. That is about 8 hours on 1.28 kWh, or under
2 hours on 286 Wh. The controller won't leave below 40% charge, and while
travelling it stops and asks for help at 15%.

## Charging is confirmed only when

Mains is present at the charger **and** current flows into the battery above
1 A, for five samples in a row. Current alone is not proof, because solar or
regeneration can push current too. A seated plug in a dead or wall-switched
outlet backs out, marks that outlet "no power", and moves on.

## Recovery and safe stop

| situation | what the robot does |
|---|---|
| battery below 40% | stays plugged in |
| plug won't come out under 70 N | pushes back in, keeps charging, asks for help |
| loads drop during unplug | stops; the power path has failed the test |
| cable won't stow | one retry, then stops without driving |
| route blocked | two tries, then the next outlet |
| outlet missing or occupied | the next outlet |
| won't seat under 60 N | backs out, three tries, then the next outlet |
| seated, no power | backs out, the next outlet |
| battery hits 15% while travelling | stops and asks for help |
| nothing worked | stops and asks for help |

Stopping means all motion off, brakes on, cord stowed or still in the wall, and a
message to Jake. The robot never pulls on a cord and never drives tethered.

## Outdoors, later

Mains only at weather-protected, GFCI outlets with in-use covers, never in rain
or standing water (a rain sensor gates it). Everything else is battery-only travel
with the pigtail sealed in its channel. Dirt on the blades and the camera window
needs a wipe step. Solar is why charge detection already requires mains present.

## Acceptance tests

Each row is a unit test in `sim/outlet_hop/test_outlet_hop.py` now, and becomes a
bench or house trial later.

| test | simulated | physical |
|---|---|---|
| full hop: unplug, drive, replug, confirm | pass | not yet |
| loads stay up under drive + compute load | pass | Stage 0 |
| low battery refuses to leave | pass | not yet |
| battery hits reserve while travelling | pass | not yet |
| power path drops loads at unplug, caught | pass | Stage 0 |
| aborted unplug keeps charging | pass | Stage 2 |
| incomplete insertion retried, then seats | pass | Stage 2 |
| never seats, moves on; retry limit held | pass | Stage 2 |
| dead outlet is not "charging" | pass | Stage 4 |
| current without mains is not "charging" | pass | Stage 4 |
| missing / occupied outlets skipped | pass | Stage 5 |
| obstruction retries, then next outlet | pass | Stage 5 |
| stow fails once, recovers; never drives tethered | pass | Stage 3 |

## Stages

0. **Power continuity, no robot.** Run the Mac mini and iPad from the candidate
   power path. Run `python3 Scripts/power_continuity_log.py --load`, pull the wall
   plug by hand for 10 minutes, plug it back, then `--report`. It passes only with
   one boot and no heartbeat gap over 0.5 s. Do this 20 times. This picks the power
   path.
1. **Simulation. Done.** `python3 -m unittest discover sim/outlet_hop`.
2. **Dead-outlet bench.** A real receptacle in a box with **no supply cord at
   all**, so it can never be live. Build the carriage and push it by hand on a
   slide first, then with a motor. Log force curves; 50 unplug and replug cycles
   across all three roll angles and a few millimetres of deliberate misaim.
3. **Carriage on the base.** Drive to the dead fixture, find it, insert, back
   out, stow. The same 50 cycles, plus blocked-route and stow failures.
4. **One supervised live outlet.** Only after Stage 3 passes. A GFCI outlet, Jake
   watching with a hand on the e-stop. Prove "charging" detection and the dead
   outlet case with a switched outlet.
5. **Two-outlet hop in the house.** The whole milestone, repeated, with the full
   test table.

## Open questions for Jake

- Which mobile base? The repo has none yet, and it sets the drive budget and
  the carriage mount.
- Is Starlink in scope for the first robot, or later?
- Try the power station first (fast), or go straight to the online path?

## Evidence

Done and verified: 16 simulated acceptance tests pass; the continuity logger
runs on this Mac (2204 heartbeats over 124 s, one boot, 80 ms worst gap, idle).
Not done: any hardware, any purchase, any physical demonstration.

Sources: EcoFlow River 3 / River 3 Plus product pages (UPS switchover claims);
Notebookcheck and Jeff Geerling on M4 Mac mini power; UL 498 withdrawal range
as cited in USPTO patent 9502808; Feetech STS3215 listings (30 kg·cm at 12 V).
