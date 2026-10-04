# Codex Image Plugin

A public Codex plugin for generating and editing raster images through an OpenAI-compatible image API. Give it an endpoint URL, an API key, and a model ID; the plugin passes the selected model through unchanged. It is not tied to one vendor or one image model.

[中文说明](README.zh-CN.md)

## Features

- Generate images with any compatible model ID.
- Edit one or more reference images and optional alpha masks.
- List models exposed by the configured endpoint.
- Inspect image-capable models exposed by the endpoint before choosing a model.
- Accept credentials from `--base-url`/`--api-key`, environment variables, or the active Codex provider.
- Never print or persist API keys. Codex session bearer tokens are not used.

## Install from GitHub

```bash
codex plugin marketplace add zlsbksdxl/gpt-image-2-skill-codex-gpt --ref main
codex plugin add codex-image-plugin@codex-image-plugin
```

Restart Codex or start a new task after installation. Invoke the skill with `$codex-image-plugin`.

## Local development

```bash
cd /Users/starfall/Project/gpt-image-2-skill-codex-gpt
python3 plugins/codex-image-plugin/skills/codex-image-plugin/scripts/image.py \
  models \
  --base-url "https://api.example.com/v1" \
  --api-key "$OPENAI_API_KEY" \
  --image-only
```

Use an environment variable for the key when possible so it does not appear in shell history. The script also reads `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and the active provider in `~/.codex/config.toml`.

## Generate with a selected model

```bash
python3 plugins/codex-image-plugin/skills/codex-image-plugin/scripts/image.py \
  generate \
  --base-url "https://api.example.com/v1" \
  --api-key "$OPENAI_API_KEY" \
  --model "gpt-image-2" \
  --prompt "A clean product photo of a ceramic mug on a white studio background" \
  --out outputs/mug.png \
  --quality high \
  --size 1024x1024 \
  --force
```

`gpt-image-2` is only an example. Use an ID returned by `models` or documented by your endpoint. The wrapper does not hardcode the model.

## Edit a reference image

```bash
python3 plugins/codex-image-plugin/skills/codex-image-plugin/scripts/image.py \
  edit \
  --base-url "https://api.example.com/v1" \
  --api-key "$OPENAI_API_KEY" \
  --model "gpt-image-2" \
  --image work/input.png \
  --prompt "Change only the background. Preserve the subject exactly: same shape, pose, proportions, colors, lighting, and details." \
  --out outputs/edited.png \
  --force
```

Repeat `--image` for multiple references. Add `--mask mask.png` for a localized edit or `--mask-ring` for a generated outer-ring mask on a square image.

## Dry-run and configuration

Add `--dry-run` to `models`, `generate`, or `edit` to inspect the endpoint and payload without making an API request. Model-specific limits for size, quality, masks, formats, and transparency are determined by the endpoint; the API response is reported directly when a request is invalid.

## License

MIT. See [LICENSE](LICENSE).
