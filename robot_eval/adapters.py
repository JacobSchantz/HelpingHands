"""Model adapters: turn one protocol observation into one action chunk.

An adapter is a class with `info` (dict), `reset()` and
`act(instruction, state, images) -> list of rows`. `images` maps "left" /
"right" to JPEG bytes. Add a model by adding a row to models.json; add an
adapter only when the model cannot be loaded by an existing one.

Only `mock` runs without a GPU. The others import torch lazily, so the Mac
client and the tests never need it.
"""
import io


class MockAdapter:
    """Holds the current pose: a safe stand-in to test cameras, transport and scoring."""

    def __init__(self, spec):
        self.chunk = int(spec.get("chunk", 10))
        self.info = {"adapter": "mock", "model": spec.get("repo", "mock"),
                     "revision": "none", "chunk": self.chunk}

    def reset(self):
        pass

    def act(self, instruction, state, images):
        return [list(state) for _ in range(self.chunk)]


def _rgb(jpeg):
    import numpy as np
    from PIL import Image
    with Image.open(io.BytesIO(jpeg)) as image:
        return np.asarray(image.convert("RGB"))


class LeRobotAdapter:
    """Any LeRobot policy (molmoact2, flux3, smolvla, pi05, groot, xvla, act ...).

    `camera_map` maps the policy's image feature keys to our cameras, e.g.
    {"observation.images.scene": "left", "observation.images.wrist": "right"};
    "blank" feeds a black frame to a view we do not have.
    A policy trained with a wrist camera is being fed a head view instead;
    the scoring sheet records the map so that is never hidden.
    """

    def __init__(self, spec, device="cuda"):
        import torch
        from lerobot.policies.factory import get_policy_class, make_pre_post_processors

        self.torch, self.device = torch, device
        self.camera_map = spec["camera_map"]
        self.policy = get_policy_class(spec["policy_type"]).from_pretrained(
            spec["repo"], revision=spec.get("revision"))
        self.policy.to(device).eval()
        override = {"device_processor": {"device": device}}
        self.pre, self.post = make_pre_post_processors(
            self.policy.config, pretrained_path=spec["repo"],
            preprocessor_overrides=override, postprocessor_overrides=override)
        missing = set(self.policy.config.image_features) - set(self.camera_map)
        if missing:
            raise ValueError(f"camera_map has no camera for {sorted(missing)}")
        self.chunk = int(spec.get("chunk", 0)) or None
        self.info = {"adapter": "lerobot", "model": spec["repo"],
                     "revision": spec.get("revision") or "main",
                     "policy_type": spec["policy_type"], "camera_map": self.camera_map}

    def reset(self):
        self.policy.reset()

    def act(self, instruction, state, images):
        torch = self.torch
        features = self.policy.config.image_features
        obs = {"observation.state": torch.tensor([state], dtype=torch.float32), "task": instruction}
        for key, feature in features.items():
            _, h, w = feature.shape
            camera = self.camera_map[key]
            if camera == "blank":
                obs[key] = torch.zeros(1, 3, h, w)
                continue
            image = torch.from_numpy(_rgb(images[camera])).permute(2, 0, 1).float() / 255
            obs[key] = torch.nn.functional.interpolate(
                image[None], size=(h, w), mode="bilinear", align_corners=False)
        with torch.inference_mode():
            chunk = self.policy.predict_action_chunk(self.pre(obs))
            if chunk.ndim == 2:
                chunk = chunk[None]
            rows = [self.post(chunk[:, i, :]) for i in range(chunk.shape[1])]
        actions = torch.cat(rows, 0).float().cpu().tolist()
        return actions[: self.chunk] if self.chunk else actions


ADAPTERS = {"mock": MockAdapter, "lerobot": LeRobotAdapter}


def load(spec):
    adapter = ADAPTERS[spec["adapter"]](spec)
    adapter.info["units"] = spec.get("units", "range")  # SO-101 range -100..100, or degrees
    return adapter
