# Helping Hands

Helping Hands builds a robot that gets real-world tasks done. This file
describes the end state. Every plan, part and script in the repo should move us
toward it. If a piece of work doesn't serve one of the two layers below, ask
why we're doing it.

## End-state architecture

**An LLM agent harness that talks to a world action model.**

```
  person: "clear the table and put the cups in the sink"
                         │
  ┌──────────────────────▼───────────────────────────────┐
  │ 2. Agent harness (LLM)                               │
  │    plans, calls tools, checks results, retries       │
  │    tools: act(instruction), look(), stop(), ...      │
  └──────────────────────┬───────────────────────────────┘
                         │ act("pick up the blue cup")
  ┌──────────────────────▼───────────────────────────────┐
  │ 1. World action model                                │
  │    trained on our gripper's data                     │
  │    cameras + instruction → action chunks             │
  └──────────────────────┬───────────────────────────────┘
                         │ joint targets
                    arm + gripper
```

### Layer 1: the world action model (low-level manipulation)

- **What it is:** one network that understands the physical world and how to
  act in it. Given the eye-height stereo views, the robot's state and a short
  instruction, it predicts what will happen and the action chunk that makes it
  happen.
- **What it's trained on:** our own gripper's data. The same gripper is
  carried in a human hand to record demonstrations and mounted on the arm to
  replay them, so the data lands in the robot's own action space. That loop
  includes the handheld gripper, glove teaching and teleop.
- **What it's responsible for:** short-horizon physical skills, such as grasp,
  place, open, pour and wipe. It is not responsible for deciding what to do
  next.
- **Today:** off-the-shelf checkpoints (MolmoAct2, FLUX 3 Action) are
  placeholders that let us build and score everything around the model. In the
  end state they're replaced by, or fine-tuned into, a model trained on our
  data.

### Layer 2: the agent harness (getting things done)

- **What it is:** an LLM agent that takes a goal in plain language, breaks it
  into steps and makes tool calls until the goal is met.
- **How it uses layer 1:** the world action model is exposed to the agent as a
  tool, the thing that executes physical actions. The agent never sends joint
  angles. It calls something like `act("pick up the blue cup")`, then looks at
  the result and decides what to do next.
- **What it's responsible for:** long-horizon planning, checking whether a step
  worked, retrying or trying a different approach, asking a person when it's
  stuck, and using non-physical tools (search, timers, messages) alongside the
  physical ones.

### The boundary between them

The contract between the two layers is a tool call: **instruction in, physical
action out, with observations to check the result.** Today that contract is the
policy-server protocol in [`robot_eval/protocol.py`](robot_eval/protocol.py)
(`POST /act` with an instruction, state and the two stereo images). Keep that
interface stable and model-agnostic so either layer can be swapped without
touching the other.

The split gives us two properties:

- **Each layer is scored on its own job.** Layer 1 on single-skill success
  (`robot_eval/`). Layer 2 on whole-task completion, including retries (see
  [`plans/agent_led_research.md`](plans/agent_led_research.md)).
- **Persistence lives in the agent, not the policy.** A skill that works 40% of
  the time is useful when the agent can see that it failed and call it again.

## How the repo maps to it

| Area | Layer | Where |
|---|---|---|
| Gripper, hand and glove hardware (the data source) | 1 | `Two Finger Gripper/`, `Three Finger Gripper/`, `cad/`, `plans/hand_1_0.md`, `plans/handheld_gripper.md`, `plans/aero-hand-glove-teaching.md` |
| Demonstration capture and training | 1 | `record_actions.sh`, `teleop.sh`, `plans/training_pipeline.md` |
| Model choice and deployment | 1 | `plans/world_action_model.md`, `plans/molmoact2_deployment.md`, `plans/robot_model_scouting.md` |
| External human data (egocentric datasets) | 1 | `plans/egocentric_datasets.md` |
| External robot data (open robot datasets) | 1 | `plans/robot_datasets.md` |
| Scoring models, the tool contract | 1 ↔ 2 | `robot_eval/` |
| Agent harness | 2 | not built yet |
| The app (instruction, eyes, stop button) | the person ↔ 2 | `HelpingHands/` |

Arm setup and calibration: [`robot_config.md`](robot_config.md).
