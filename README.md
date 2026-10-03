# GPT Image 2 for Codex

A small, installable Codex plugin for generating and editing raster images with GPT Image 2. It packages the `gpt-image-2` Skill and a safe local wrapper that reads the active Codex provider configuration without printing or persisting API keys.

[中文说明](README.zh-CN.md)

## Features

- Text-to-image generation with `gpt-image-2`.
- Edits with one or more reference images.
- Localized edits with an alpha PNG mask, including a generated ring mask for square images.
- Prompt helpers for use case, style, composition, and constraints.
- `--dry-run` validation before a paid API request.
- No hard-coded credentials and no use of Codex session bearer tokens.

## Install from GitHub

```bash
codex plugin marketplace add zlsbksdxl/gpt-image-2-skill-codex-gpt --ref main
codex plugin add gpt-image-2-codex@gpt-image-2-skill-codex-gpt
```

Restart Codex or start a new task after installation. Invoke it explicitly with `$gpt-image-2`, or describe an image-generation or image-editing request normally.

## Local development

The repository can live anywhere. For the author's local checkout:

```bash
cd /Users/starfall/Project/gpt-image-2-skill-codex-gpt
```

To test the skill source without installing it globally:

```bash
python3 plugins/gpt-image-2-codex/skills/gpt-image-2/scripts/image.py generate \
  --prompt "A clean architectural visualization" \
  --out outputs/architecture.png \
  --dry-run
```

## Configuration

The wrapper reads the active provider from `~/.codex/config.toml`:

```toml
model_provider = "OpenAI"

[model_providers.OpenAI]
OPENAI_API_KEY = "your-image-api-key"
base_url = "https://api.openai.com/v1"
```

The key may instead be supplied as `OPENAI_API_KEY`, and the endpoint as `OPENAI_BASE_URL`. A configured endpoint may be an OpenAI-compatible gateway. The wrapper never reads or reuses `experimental_bearer_token`.

The local Codex ImageGen runtime must be available at `~/.codex/skills/.system/imagegen/scripts/image_gen.py`, or at the path passed with `--image-gen`.

## Generate an image

```bash
python3 plugins/gpt-image-2-codex/skills/gpt-image-2/scripts/image.py generate \
  --prompt "A clean product photo of a ceramic mug on a white studio background" \
  --out outputs/mug.png \
  --quality high \
  --size 1024x1024 \
  --force
```

Useful optional flags: `--use-case`, `--style`, `--composition`, `--constraints`, and `--dry-run`.

## Edit an image

```bash
python3 plugins/gpt-image-2-codex/skills/gpt-image-2/scripts/image.py edit \
  --image work/input.png \
  --prompt "Change only the background. Preserve the subject exactly: same shape, pose, proportions, colors, lighting, and details." \
  --out outputs/edited.png \
  --quality high \
  --size 1024x1024 \
  --force
```

Repeat `--image` for multiple references. Add `--mask mask.png` for a localized edit. The mask must be a PNG with alpha; transparent pixels are editable and opaque pixels are preserved. `--mask-ring` creates a temporary ring mask for a square image.

## Limitations

- GPT Image 2 does not provide true transparent-background output through this workflow. Generate against a plain or chroma background, then remove it locally if alpha is required.
- Image edits can reinterpret protected content. Use a precise preservation prompt and a mask when pixel-level preservation matters.
- Image generation and editing use API billing from the configured provider. Run `--dry-run` first when checking a new setup.

## License

MIT. See [LICENSE](LICENSE).
