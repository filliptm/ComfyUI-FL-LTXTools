"""VAE patching helpers for LTX-Video."""

import copy
import logging

logger = logging.getLogger(__name__)


def clone_vae_with_decoder_noise(vae, decode_noise_scale: float, decode_timestep: float):
    """Return a clone of the VAE with decode_noise_scale and decode_timestep
    overridden on the inner causal_video_autoencoder.

    Falls back to returning the original VAE (with a warning) if it doesn't
    look like an LTX VAE.
    """
    inner = getattr(vae, "first_stage_model", None)
    if inner is None:
        logger.warning("FL_LTX_MotionBoost: VAE has no first_stage_model — passthrough.")
        return vae

    has_decode_noise = hasattr(inner, "decode_noise_scale")
    has_decode_timestep = hasattr(inner, "decode_timestep")
    if not (has_decode_noise and has_decode_timestep):
        logger.warning(
            "FL_LTX_MotionBoost: VAE first_stage_model is not an LTX CausalVideoAutoencoder "
            "(missing decode_noise_scale / decode_timestep attributes) — passthrough."
        )
        return vae

    # Shallow clone the outer wrapper, then deepcopy just the inner model so we
    # don't mutate the user's existing VAE reference. The outer wrapper's other
    # attributes (memory_used_decode, dtype, etc.) are kept by reference.
    vae_clone = copy.copy(vae)
    inner_clone = copy.copy(inner)
    inner_clone.decode_noise_scale = float(decode_noise_scale)
    inner_clone.decode_timestep = float(decode_timestep)
    vae_clone.first_stage_model = inner_clone
    return vae_clone
