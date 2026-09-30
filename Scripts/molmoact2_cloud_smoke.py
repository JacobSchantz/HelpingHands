# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = [
#   "torch==2.11.0", "torchvision==0.26.0", "transformers==5.3.0",
#   "accelerate>=1,<2", "pillow>=10,<13", "numpy>=1.26,<3",
#   "einops>=0.7,<1", "sentencepiece>=0.2,<1", "protobuf>=4.25,<7",
#   "huggingface-hub>=1,<2",
# ]
# ///
"""GPU-only inference check on public sample images. Never controls a robot.

Launch with a bounded HF Job; see plans/molmoact2_deployment.md.
"""
import json
import time

REPO = "allenai/MolmoAct2-SO100_101"
REVISION = "152569fe57914d97be91055800035f54e250d009"


def main():
    import numpy as np
    import torch
    from huggingface_hub import hf_hub_download
    from PIL import Image
    from transformers import AutoModelForImageTextToText, AutoProcessor

    if not torch.cuda.is_available():
        raise RuntimeError("This cloud smoke test requires an NVIDIA GPU")
    print(json.dumps({"event": "loading", "model": REPO,
                      "revision": REVISION, "gpu": torch.cuda.get_device_name()}), flush=True)
    processor = AutoProcessor.from_pretrained(REPO, revision=REVISION, trust_remote_code=True)
    model = AutoModelForImageTextToText.from_pretrained(
        REPO, revision=REVISION, trust_remote_code=True,
        dtype=torch.bfloat16,
    ).to("cuda").eval()
    images = []
    for name in ("sample_realsense_top_rgb.png", "sample_realsense_side_rgb.png"):
        path = hf_hub_download(REPO, "assets/" + name, revision=REVISION)
        with Image.open(path) as image:
            images.append(image.convert("RGB"))
    state = np.array([-0.52734375, 189.140625, 181.40625,
                      60.64453125, -3.603515625, 1.0971786975860596], dtype=np.float32)
    timings = []
    torch.manual_seed(0)
    for iteration in range(4):
        torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
            result = model.predict_action(
                processor=processor, images=images, state=state,
                task="Move the arm towards the lemon, grasp it, lift it up, and drop it into the red bowl.",
                norm_tag="so100_so101_molmoact2", inference_action_mode="continuous",
                enable_depth_reasoning=False, enable_cuda_graph=False, num_steps=10,
            )
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        actions = result.actions
        if isinstance(actions, torch.Tensor):
            actions = actions.detach().float().cpu().numpy()
        actions = np.asarray(actions)
        if actions.ndim not in (2, 3) or actions.shape[-1] != 6 or not actions.size or not np.isfinite(actions).all():
            raise RuntimeError(f"Invalid SO-101 action output: shape={actions.shape}")
        timings.append(elapsed)
        print(json.dumps({"event": "prediction", "iteration": iteration,
                          "seconds": elapsed, "shape": list(actions.shape)}), flush=True)
    print(json.dumps({"event": "passed", "warm_seconds": timings[1:],
                      "peak_gpu_gib": torch.cuda.max_memory_allocated() / 2**30,
                      "hardware_motion_tested": False,
                      "head_camera_tested": False}), flush=True)


if __name__ == "__main__":
    main()
