# Tool Caddy — a robot that hands you power tools

Status: CONCEPT (this document + `tool-caddy-render.png`, modeled in Blender).

## The idea

A mobile robot built around three things:

1. **A Mac Mini as the brain** — it runs the vision model (sees which tool is
   which, where you are), the speech stack (you say "hand me the drill" —
   Pebbles is the natural front door for this), and the arm policy.
2. **A battery pack** — LiFePO4, sized for a shift: it powers the Mini, the
   base motors, and recharges tool batteries in its dock, so the cart is
   genuinely untethered.
3. **A tool cart** — a rolling utility cart with a rack of power tools
   (drill, impact driver, circular saw, spare batteries), each in a marked
   dock the arm can grip from.

On top sits an **SO-101 arm** (the same leader/follower hardware already in
this repo) whose job is exactly one thing: pick the tool you asked for out of
its dock and hand it to you, then take it back when you're done.

## Layout (matching the render)

| part | where | notes |
|---|---|---|
| SO-101 arm | top shelf, rear | gripper rest position over the tool rack |
| drill (in gripper) | top shelf | the "hand-off" pose shown in the render |
| Mac Mini | middle shelf, front | vents face outward; runs headless |
| LiFePO4 battery | middle shelf, rear | terminals + charger board |
| power strip | side post | one switched outlet per dock (tool recharging) |
| circular saw, impact driver, spares | bottom shelf | docks marked for vision |
| casters + handle | base | motorized later; hand-push for v1 |

## How a hand-off works (v1, no autonomy)

1. You say "Pebbles, hand me the drill" (Pebbles already hears you anywhere).
2. The Mac Mini looks up the tool's dock, the arm grips it (fixed poses,
   recorded with the existing `record_actions.sh` teleop pipeline).
3. The cart drives to you (v2) or you walk to the cart (v1).
4. You pull the tool from the gripper; the arm returns to rest.

## Phases

1. **v1 — static caddy**: cart + arm + Mini, docks marked, hand-off by
   recorded poses. Voice trigger via Pebbles. No driving.
2. **v2 — mobility**: motorize the base, add a line-follow or tag-follow so
   the cart comes to you.
3. **v3 — vision**: the Mini identifies tools and hand positions, so docks
   get loose and the grip gets reliable anywhere on the rack.

## Open questions

- Base: motorize the existing cart casters vs. a off-the-shelf AGV chassis?
- Arm reach is ~30cm — does the hand-off pose need a second DOF stage?
- Battery budget: Mini idle draw vs. shift length (measure before sizing).
