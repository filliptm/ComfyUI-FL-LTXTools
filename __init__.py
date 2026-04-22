"""ComfyUI-FL-LTXTools: Experimental tools and motion controls for LTX-Video."""

import logging

logger = logging.getLogger("FL_LTXTools")

try:
    from .nodes import FL_LTX_MotionBoost

    NODE_CLASS_MAPPINGS = {
        "FL_LTX_MotionBoost": FL_LTX_MotionBoost,
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "FL_LTX_MotionBoost": "FL LTX Motion Boost",
    }

    __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

    print("\033[92m[ComfyUI-FL-LTXTools] Loaded successfully! Nodes: Motion Boost\033[0m")

except Exception as e:
    logger.error(f"Failed to load FL_LTXTools nodes: {e}")
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}
