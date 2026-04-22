"""FL LTX Motion Boost — single-knob motion intensity control for LTX-Video."""

import logging

import node_helpers

from ..modules.vae_patcher import clone_vae_with_decoder_noise

logger = logging.getLogger(__name__)


class FL_LTX_MotionBoost:
    """Boost or reduce motion intensity for LTX-Video.

    Drives two motion levers simultaneously:
      1. Conditioning frame_rate (lower fps -> wider RoPE temporal gaps -> bigger motion per frame)
      2. VAE decode noise (decode_noise_scale + decode_timestep -> per-frame organic stochasticity)

    Place between LTX conditioning (positive/negative) and the sampler/VAE decode.
    """

    CATEGORY = "FL LTX Tools/Motion"
    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "VAE")
    RETURN_NAMES = ("positive", "negative", "vae")
    FUNCTION = "boost"
    DESCRIPTION = (
        "Single-knob motion control for LTX-Video. motion_intensity adjusts the "
        "conditioning frame_rate to widen/narrow temporal RoPE gaps (the primary motion lever). "
        "decode_noise/decode_timestep control VAE-side per-frame stochasticity."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "vae": ("VAE",),
                "motion_intensity": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.05,
                        "tooltip": (
                            "0.0 = static (no motion boost), 0.5 = balanced default, "
                            "1.0 = maximum motion (lowers frame_rate ~60%)."
                        ),
                    },
                ),
                "decode_noise": (
                    "FLOAT",
                    {
                        "default": 0.025,
                        "min": 0.0,
                        "max": 0.5,
                        "step": 0.005,
                        "tooltip": (
                            "VAE decode noise scale. Adds organic per-frame stochasticity. "
                            "0.025 is the LTX default. Higher = more textural noise + smoother motion."
                        ),
                    },
                ),
                "decode_timestep": (
                    "FLOAT",
                    {
                        "default": 0.05,
                        "min": 0.0,
                        "max": 0.5,
                        "step": 0.005,
                        "tooltip": (
                            "VAE decode noise timestep. 0.05 is the LTX default."
                        ),
                    },
                ),
            },
            "optional": {
                "base_frame_rate": (
                    "INT",
                    {
                        "default": 25,
                        "min": 6,
                        "max": 60,
                        "step": 1,
                        "tooltip": (
                            "Reference fps before motion_intensity scaling. "
                            "Final fps = base_frame_rate * (1.0 - motion_intensity * 0.6)."
                        ),
                    },
                ),
                "override_frame_rate": (
                    "INT",
                    {
                        "default": -1,
                        "min": -1,
                        "max": 60,
                        "step": 1,
                        "tooltip": (
                            "If >= 6, sets the conditioning frame_rate explicitly and ignores "
                            "motion_intensity for this lever. -1 = auto."
                        ),
                    },
                ),
            },
        }

    def boost(
        self,
        positive,
        negative,
        vae,
        motion_intensity: float,
        decode_noise: float,
        decode_timestep: float,
        base_frame_rate: int = 25,
        override_frame_rate: int = -1,
    ):
        # Compute target fps
        if override_frame_rate is not None and override_frame_rate >= 6:
            target_fps = float(override_frame_rate)
        else:
            # motion_intensity 0.0 -> base_frame_rate (no boost)
            # motion_intensity 1.0 -> base_frame_rate * 0.4 (max boost)
            scale = 1.0 - (float(motion_intensity) * 0.6)
            target_fps = max(1.0, float(base_frame_rate) * scale)

        # Patch conditioning with new frame_rate (matches built-in LTXVConditioning pattern)
        positive = node_helpers.conditioning_set_values(positive, {"frame_rate": target_fps})
        negative = node_helpers.conditioning_set_values(negative, {"frame_rate": target_fps})

        # Patch VAE with decoder noise settings
        vae = clone_vae_with_decoder_noise(vae, decode_noise, decode_timestep)

        logger.info(
            f"[FL_LTX_MotionBoost] motion_intensity={motion_intensity:.2f} "
            f"-> frame_rate={target_fps:.2f}, decode_noise={decode_noise:.3f}, "
            f"decode_timestep={decode_timestep:.3f}"
        )

        return (positive, negative, vae)
