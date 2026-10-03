---
name: gpt-image-2
description: Generate or edit raster images with GPT Image 2 through the local Codex configuration. Use for new images, reference-image edits, multi-image compositing, masked edits, cleanup, sharpening, background changes, mockups, illustrations, and avatar or logo bitmap drafts.
---

# GPT Image 2

Use the bundled `scripts/image.py` wrapper. It reads the active Codex provider's `OPENAI_API_KEY` (or `api_key`) and optional `base_url` from `~/.codex/config.toml`, then invokes Codex's local ImageGen runtime with model `gpt-image-2`. It may also use `OPENAI_API_KEY` and `OPENAI_BASE_URL` from the environment. Never print, persist, or reuse a Codex session bearer token as an image API key.

## Workflow

1. Classify the request as `generate` or `edit`.
2. For an edit, obtain the actual input file before invoking the script. Keep user-provided files unchanged and write a new result by default.
3. Save user-facing results under the current workspace `outputs/` directory unless the user requests another path.
4. Inspect the result. Check composition, exact text, file format, and any protected subject or region. If the subject changed, tighten the preservation prompt or use a mask.
5. Report the exact output path and any model or input limitation.

## Generate

```bash
python3 <plugin-root>/skills/gpt-image-2/scripts/image.py generate \
  --prompt "A clean product photo of a ceramic mug on a white studio background" \
  --out outputs/mug.png \
  --quality high \
  --size 1024x1024 \
  --force
```

Optional prompt-shaping flags are `--use-case`, `--style`, `--composition`, and `--constraints`.

## Edit

```bash
python3 <plugin-root>/skills/gpt-image-2/scripts/image.py edit \
  --image work/input.png \
  --prompt "Remove the background. Preserve the subject exactly: same shape, pose, proportions, colors, lighting, and details." \
  --out outputs/edited.png \
  --quality high \
  --size 1024x1024 \
  --force
```

Repeat `--image` for multiple references. Use `--mask mask.png` for localized edits. A mask must be a PNG with alpha: transparent pixels are editable and opaque pixels are preserved. `--mask-ring` creates a temporary ring mask for a square image.

## Prompting

Separate mutable and protected content. For a localized edit, say exactly what may change and preserve the subject's shape, pose, proportions, colors, line style, lighting, and details. For a new image, specify the asset type, subject, setting, composition, style, lighting, exact text, and constraints. Do not promise native transparent output: GPT Image 2 requires a plain or chroma background for this workflow, followed by local background removal when needed.

Use `--dry-run` to validate the command and payload without making an API call.
