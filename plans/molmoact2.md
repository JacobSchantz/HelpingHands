# MolmoAct2 — VLA north star for Helping Hands

Status: REFERENCE (upstream repo linked, no weights vendored here).

Upstream: https://github.com/allenai/molmoact2

## What it is

MolmoAct2 is Ai2's open family of action reasoning models for robot
control and real-world deployment. It builds on the Molmo2-ER
embodied-reasoning vision-language backbone, adds robot state and action
modeling, and connects to a flow-matching continuous action expert for
closed-loop manipulation.

- License: Apache-2.0
- Blog: https://allenai.org/blog/molmoact2
- Paper: https://arxiv.org/abs/2605.02881
- Base checkpoints: https://huggingface.co/collections/allenai/molmoact2-models-69f81e05242e2499606b1be6
- Fine-tuned checkpoints: https://huggingface.co/collections/allenai/molmoact2-finetuned-models-69f81e23d5a7b34fde34f2ce
- Datasets: https://huggingface.co/collections/allenai/molmoact2-datasets-69f81e316ec3daafe3f9555c
- LeRobot docs: https://huggingface.co/docs/lerobot/main/en/molmoact2

## Why it matters here

Helping Hands runs SO-101 leader/follower arms on LeRobot
(`robot_config.md`, `teleop.sh`, `record_actions.sh`,
`lerobot_calibration/`). MolmoAct2 ships explicit SO-100/101 support,
a LeRobot policy integration, and a fine-tuned checkpoint for
SO-100/SO-101:

- Checkpoint: https://huggingface.co/allenai/MolmoAct2-SO100_101
- Real-world deployment notes: see upstream `README.md`
  section "4. Real-world Deployment / SO-100/101 Setup"
- LeRobot integration lives upstream as a git submodule at `lerobot/`,
  pinned to `allenai/lerobot:molmoact2-policy`

This matches the Helping Hands north star already recorded in
`pebbles/agent/voice-4858e8fa/pebble.json`: vision-language-action
models doing real manipulation zero-shot from a camera plus a
natural-language instruction, with no task-specific dataset.

## What we do NOT vendor here

- No model weights
- No datasets
- No upstream code copy

This file is a pointer only. Fetch weights from Hugging Face and code
from upstream when needed.

## Suggested next steps

1. Read the blog + paper for the action-reasoning claim.
2. Try upstream zero-shot eval on ManiSkill sim before touching hardware:
   see upstream `sim_eval/`.
3. Try the SO-101 fine-tuned checkpoint against our calibration
   (`lerobot_calibration/follower_right.json`, `leader_left.json`)
   with a simple pick-and-place, per `plans/training_pipeline.md`.
4. If a VLA does perception + action planning, redefine this app's job:
   what we capture and send (camera + language), what UI remains,
   and what changes in `HelpingHands/Plans/` and `Scripts/`.
