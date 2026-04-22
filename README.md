# FL LTX Tools

Experimental tools and motion controls for [LTX-Video](https://github.com/Lightricks/LTX-Video) in ComfyUI. Designed to drop into existing LTX workflows with minimal wiring.

[![LTX-Video](https://img.shields.io/badge/LTX--Video-Original%20Repo-blue?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Lightricks/LTX-Video)
[![Patreon](https://img.shields.io/badge/Patreon-Support%20Me-F96854?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/Machinedelusions)

## Features

- **Single-knob motion control** — one `motion_intensity` slider that drives multiple underlying LTX motion levers
- **VAE decoder noise control** — exposes `decode_noise_scale` and `decode_timestep` for per-frame stochasticity
- **Drop-in replacement** for the built-in `LTXVConditioning` node — same conditioning pattern, with motion boost on top
- **Self-contained** — no dependency on other LTX custom node packs

## Nodes

| Node | Description |
|------|-------------|
| **FL LTX Motion Boost** | Drives motion via conditioning frame_rate (RoPE temporal scale) + VAE decoder noise. Inputs: positive/negative cond + VAE. Outputs: patched cond + VAE. |

## Installation

### ComfyUI Manager
Search for "FL LTX Tools" and install.

### Manual
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/filliptm/ComfyUI-FL-LTXTools.git
cd ComfyUI-FL-LTXTools
pip install -r requirements.txt
```

## Quick Start

1. Build a normal LTX-Video workflow (model loader, text encode, empty latent, sampler, VAE decode)
2. Insert **FL LTX Motion Boost** between your text encoders and the sampler
3. Wire `positive`, `negative`, and `vae` through it
4. Adjust `motion_intensity` (0.0 = static, 0.5 = balanced, 1.0 = chaotic)

## How It Works

LTX-Video has no single "motion intensity" knob — motion behavior emerges from the interaction of multiple parameters. This node consolidates the most reliable motion lever (conditioning frame_rate via RoPE temporal embeddings) with VAE-side stochasticity into a single intuitive control.

### motion_intensity

Maps to the conditioning `frame_rate` value:
- `0.0` → uses `base_frame_rate` (default 25 fps) — no motion boost
- `0.5` → ~17 fps — moderate boost (LTX interprets each frame as a larger temporal step)
- `1.0` → ~10 fps — heavy boost, dramatic motion per frame

Lower frame_rate values widen the gaps between RoPE temporal positions, so the model "thinks" each output frame represents a longer time slice. Result: more motion happens between frames.

### decode_noise + decode_timestep

VAE decoder noise injection. Adds Gaussian stochasticity at decode time:
- Higher noise → smoother, more organic motion textures
- Lower noise → crisper but potentially jittery output
- LTX defaults: `decode_noise = 0.025`, `decode_timestep = 0.05`

## Inputs

| Name | Type | Range | Default | Description |
|------|------|-------|---------|-------------|
| `positive` | CONDITIONING | — | — | Positive conditioning |
| `negative` | CONDITIONING | — | — | Negative conditioning |
| `vae` | VAE | — | — | LTX VAE |
| `motion_intensity` | FLOAT | 0.0–1.0 | 0.5 | Motion boost amount |
| `decode_noise` | FLOAT | 0.0–0.5 | 0.025 | VAE decode noise scale |
| `decode_timestep` | FLOAT | 0.0–0.5 | 0.05 | VAE decode noise timestep |
| `base_frame_rate` | INT (optional) | 6–60 | 25 | Reference fps before scaling |
| `override_frame_rate` | INT (optional) | -1, 6–60 | -1 | Set explicit fps, ignore motion_intensity |

## Outputs

`(positive, negative, vae)` — drop into your sampler / VAE decode chain.

## Roadmap

More LTX experiments planned. Potential additions:
- STG (Spatiotemporal Skip Guidance) helper
- Motion preset library (cinematic, action, dialogue, etc.)
- Latent noise manipulation utilities

## License

[Apache-2.0](LICENSE) — Built on top of [Lightricks LTX-Video](https://github.com/Lightricks/LTX-Video).
