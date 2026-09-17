#!/usr/bin/env bash
# =============================================================================
# LeHome simulation bootstrap — zero to "watch it fold" on a fresh Linux box
# =============================================================================
#
# Reproduces Ilia Larchenko's prizewinning LeHome Challenge 2026 policy in
# NVIDIA Isaac Sim, using his RELEASED checkpoint. No training, no robot, no
# arms, no cameras. Just the simulator and the downloaded policy.
#
# THIS CANNOT RUN ON macOS. Isaac Sim 5.1 ships x86_64 builds for Ubuntu
# 22.04/24.04 and Windows only (plus an aarch64 build restricted to NVIDIA DGX
# Spark), and the policy server needs jax[cuda12] on an NVIDIA GPU. There is no
# Apple Silicon path for either half. Run this on a rented or owned Linux box.
#
# TARGET MACHINE (hard minimums, from NVIDIA's Isaac Sim 5.1 requirements page
# and this repo's own pyproject/setup.sh):
#   OS       Ubuntu 22.04 or 24.04, x86_64
#   GPU      NVIDIA with RT cores and >= 16 GB VRAM (RTX 4080/4090/5090,
#            RTX 6000 Ada, RTX PRO 6000, L40S).
#            A100 and H100 are NOT supported — they have no RT cores and Isaac
#            Sim's renderer refuses them. Do not rent one for this.
#   Driver   >= 580.65.06
#   CPU      >= 16 cores. The garment cloth physics runs on CPU (eval_worker.py
#            hardcodes `--device cpu` for the Isaac Sim process), so core count
#            sets rollout throughput, not the GPU.
#   RAM      >= 32 GB
#   Disk     >= 150 GB free
#
# USAGE (on the target machine):
#   bash lehome_sim_bootstrap.sh            # full: install, download, evaluate
#   bash lehome_sim_bootstrap.sh --setup    # stop after install + assets
#   bash lehome_sim_bootstrap.sh --eval     # skip install, just evaluate
#
# WHAT IT DOWNLOADS (~12 GB, all public — no HF token needed):
#   1.0 GB   lehome/asset_challenge          garment meshes + scenes
#  10.5 GB   IliaLarchenko/lehome_sim        the 1st-place sim-round policy
# It deliberately does NOT download the 18.9 GB behavioural-cloning dataset —
# that is only needed to TRAIN. Running the released policy does not touch it.
# =============================================================================

set -euo pipefail

REPO_DIR="${LEHOME_DIR:-$HOME/lehome_solution}"
DO_SETUP=true
DO_EVAL=true
for arg in "$@"; do
    case "$arg" in
        --setup) DO_EVAL=false ;;
        --eval)  DO_SETUP=false ;;
        -h|--help) sed -n '2,50p' "$0"; exit 0 ;;
    esac
done

say() { echo ""; echo "=== $1 ==="; }

# ---------------------------------------------------------------------------
# 0. Refuse to run anywhere it cannot possibly work, with a real explanation.
# ---------------------------------------------------------------------------
say "0. Preflight"
[ "$(uname -s)" = "Linux" ] || {
    echo "FATAL: this is $(uname -s), not Linux."
    echo "Isaac Sim 5.1 has no macOS build. Run this on Ubuntu 22.04/24.04 x86_64."
    exit 1; }
[ "$(uname -m)" = "x86_64" ] || {
    echo "FATAL: this is $(uname -m). Isaac Sim's only aarch64 build is DGX-Spark-only."
    exit 1; }
command -v nvidia-smi >/dev/null || {
    echo "FATAL: no nvidia-smi. An NVIDIA GPU with RT cores is required."
    exit 1; }
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
case "$GPU_NAME" in
    *A100*|*H100*|*H200*)
        echo ""
        echo "FATAL: $GPU_NAME has no RT cores. NVIDIA lists A100/H100 as"
        echo "unsupported for Isaac Sim. Rent an RTX 4090 / 5090 / 6000 Ada"
        echo "/ PRO 6000 / L40S instead."
        exit 1 ;;
esac
VRAM_MB="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)"
[ "$VRAM_MB" -ge 15000 ] || echo "  WARNING: ${VRAM_MB}MB VRAM is below the 16 GB minimum."
FREE_GB="$(df -BG --output=avail "$HOME" | tail -1 | tr -dc '0-9')"
[ "$FREE_GB" -ge 150 ] || echo "  WARNING: only ${FREE_GB}GB free; 150 GB recommended."
echo "  CPU cores: $(nproc)   RAM: $(free -g | awk '/^Mem:/{print $2}')GB   Free disk: ${FREE_GB}GB"

# ---------------------------------------------------------------------------
# 1. Clone with submodules. openpi and lehome-challenge are submodules; a
#    plain clone leaves them empty and setup.sh then re-clones them by hand.
# ---------------------------------------------------------------------------
if [ "$DO_SETUP" = true ]; then
    say "1. Clone lehome_solution (+ openpi, lehome-challenge submodules)"
    if [ -d "$REPO_DIR/.git" ]; then
        echo "  Already at $REPO_DIR — updating submodules."
        git -C "$REPO_DIR" submodule update --init --recursive
    else
        git clone --recurse-submodules \
            https://github.com/IliaLarchenko/lehome_solution "$REPO_DIR"
    fi

    # ---------------------------------------------------------------------
    # 2. The upstream installer. Installs apt deps, uv, both venvs, Isaac Sim
    #    5.1, the lehome-official IsaacLab fork, and the 1.0 GB garment
    #    assets. Expect 30-60 minutes.
    #
    #    NOTE: do NOT pass --no-data here. That flag also skips the garment
    #    meshes, which the evaluation needs. The 18.9 GB BC dataset is a
    #    separate step (scripts/download_hf_assets.py) that we never run.
    # ---------------------------------------------------------------------
    say "2. Run upstream setup.sh (apt + uv + Isaac Sim + IsaacLab + assets)"
    cd "$REPO_DIR"
    bash setup.sh --no-tests

    # ---------------------------------------------------------------------
    # 3. The released 1st-place simulation policy. Public, no token needed.
    # ---------------------------------------------------------------------
    say "3. Download the lehome_sim checkpoint (10.5 GB)"
    if [ -d "$REPO_DIR/outputs/checkpoints/lehome_sim/params" ]; then
        echo "  Already downloaded."
    else
        cd "$REPO_DIR"
        uv run hf download IliaLarchenko/lehome_sim \
            --local-dir outputs/checkpoints/lehome_sim
    fi
fi

# ---------------------------------------------------------------------------
# 4. Evaluate. run_eval.py starts its own policy server and launches N Isaac
#    Sim workers. Workers are CPU-bound on cloth physics, so scale by cores.
# ---------------------------------------------------------------------------
if [ "$DO_EVAL" = true ]; then
    cd "$REPO_DIR"
    WORKERS="${LEHOME_WORKERS:-$(( $(nproc) / 6 ))}"
    [ "$WORKERS" -lt 1 ] && WORKERS=1
    [ "$WORKERS" -gt 4 ] && WORKERS=4

    say "4a. Fast benchmark — success rates only, no videos ($WORKERS workers)"
    uv run python scripts/run_eval.py \
        --checkpoint_dir outputs/checkpoints/lehome_sim \
        --config_name pi_modified_bc_rl \
        --num_workers "$WORKERS" --all \
        --num_episodes 2 --metrics_only --no_wandb

    # Expect 80%+ average success on the seen garments, a bit lower on unseen.
    # If it lands far below that, the install is wrong — do not start tuning.

    say "4b. One garment with video, so there is something to actually watch"
    uv run python scripts/run_eval.py \
        --checkpoint_dir outputs/checkpoints/lehome_sim \
        --config_name pi_modified_bc_rl \
        --num_workers 1 --garment_types top_long \
        --num_episodes 2 --no_wandb

    say "Done"
    echo "  Metrics: $REPO_DIR/outputs/eval_videos/*/eval_summary.txt"
    echo "  Videos:  $REPO_DIR/outputs/eval_videos/"
    echo ""
    echo "  Pull the videos back with:"
    echo "    rsync -av <host>:$REPO_DIR/outputs/eval_videos/ ./lehome_eval/"
fi
