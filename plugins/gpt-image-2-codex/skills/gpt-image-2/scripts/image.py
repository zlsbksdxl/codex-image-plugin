#!/usr/bin/env python3
"""Run Codex's local ImageGen runtime with GPT Image 2.

The wrapper reads only an image API key and optional endpoint from the active
Codex provider. It never prints or persists credential values.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 and older
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ModuleNotFoundError:  # pragma: no cover - dependency-free fallback
        tomllib = None  # type: ignore[assignment]

DEFAULT_MODEL = "gpt-image-2"


def die(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def _strip_inline_comment(value: str) -> str:
    quoted = False
    quote = ""
    for index, char in enumerate(value):
        if char in {"'", '"'}:
            if not quoted:
                quoted = True
                quote = char
            elif quote == char:
                quoted = False
        elif char == "#" and not quoted:
            return value[:index].rstrip()
    return value.strip()


def _parse_scalar(value: str) -> Any:
    value = _strip_inline_comment(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value


def _parse_minimal_toml(text: str) -> dict[str, Any]:
    """Parse the simple string sections needed on Python versions without tomllib."""
    root: dict[str, Any] = {}
    section: dict[str, Any] = root
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = root
            for part in line[1:-1].split("."):
                section = section.setdefault(part, {})
            continue
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        section[key.strip()] = _parse_scalar(raw_value)
    return root


def _load_config(config: Path) -> dict[str, Any]:
    if not config.exists():
        return {}
    try:
        text = config.read_text(encoding="utf-8")
        if tomllib is not None:
            return tomllib.loads(text)
        return _parse_minimal_toml(text)
    except (OSError, ValueError) as exc:
        die(f"could not read Codex config {config}: {exc}")
    return {}  # unreachable


def read_codex_openai_config(config: Path) -> tuple[str | None, str | None]:
    data = _load_config(config)
    providers = data.get("model_providers", {})
    if not isinstance(providers, dict):
        providers = {}
    active = data.get("model_provider")
    candidates: list[str] = []
    if isinstance(active, str) and active:
        candidates.append(active)
    if "OpenAI" not in candidates:
        candidates.append("OpenAI")

    for name in candidates:
        provider = providers.get(name)
        if not isinstance(provider, dict):
            continue
        key = provider.get("OPENAI_API_KEY") or provider.get("api_key")
        base_url = provider.get("base_url")
        if key or base_url:
            return (str(key) if key else None, str(base_url) if base_url else None)

    return None, None


def common_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--out", required=True, help="Output image path")
    parser.add_argument("--prompt", required=True, help="Image generation or edit prompt")
    parser.add_argument(
        "--config",
        default=str(Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "config.toml"),
        help="Codex config path (default: $CODEX_HOME/config.toml)",
    )
    parser.add_argument(
        "--image-gen",
        default=str(
            Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
            / "skills/.system/imagegen/scripts/image_gen.py"
        ),
        help="Path to Codex's local ImageGen runtime",
    )
    parser.add_argument("--model", default=os.environ.get("GPT_IMAGE_MODEL", DEFAULT_MODEL))
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GPT Image models using Codex configuration.")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate", help="Generate an image from text")
    common_parser(generate)
    generate.add_argument("--use-case", default=None)
    generate.add_argument("--style", default=None)
    generate.add_argument("--composition", default=None)
    generate.add_argument("--constraints", default=None)

    edit = sub.add_parser("edit", help="Edit one or more input images")
    common_parser(edit)
    edit.add_argument("--image", required=True, action="append", help="Input image path; repeat for multiple references")
    edit.add_argument("--mask", default=None, help="Optional mask PNG; transparent pixels are editable")
    edit.add_argument("--mask-ring", action="store_true", help="Create a temporary ring mask for an outer border")
    return parser


def append_optional(cmd: list[str], flag: str, value: str | None) -> None:
    if value:
        cmd.extend([flag, value])


def make_ring_mask(image: Path, mask: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on runtime
        die(f"Pillow is required for --mask-ring: {exc}")

    im = Image.open(image).convert("RGBA")
    width, height = im.size
    side = min(width, height)
    pad_outer = side * 0.075
    pad_inner = side * 0.115
    cx, cy = width / 2, height / 2
    outer = (
        cx - side / 2 + pad_outer,
        cy - side / 2 + pad_outer,
        cx + side / 2 - pad_outer,
        cy + side / 2 - pad_outer,
    )
    inner = (
        cx - side / 2 + pad_inner,
        cy - side / 2 + pad_inner,
        cx + side / 2 - pad_inner,
        cy + side / 2 - pad_inner,
    )
    alpha = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(alpha)
    draw.ellipse(outer, fill=0)
    draw.ellipse(inner, fill=255)
    alpha = alpha.filter(ImageFilter.GaussianBlur(max(0.5, side / 180)))
    output = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    output.putalpha(alpha)
    mask.parent.mkdir(parents=True, exist_ok=True)
    output.save(mask)


def main() -> None:
    args = build_parser().parse_args()
    image_gen = Path(args.image_gen).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    if not image_gen.exists():
        die(f"image_gen.py not found: {image_gen}")

    api_key, base_url = read_codex_openai_config(Path(args.config).expanduser())
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    if not api_key and not args.dry_run:
        die("OPENAI_API_KEY is missing in the active Codex provider and environment")

    cmd = [
        sys.executable,
        str(image_gen),
        args.command,
        "--model",
        args.model,
        "--prompt",
        args.prompt,
        "--quality",
        args.quality,
        "--size",
        args.size,
        "--out",
        str(out),
    ]

    if args.command == "generate":
        append_optional(cmd, "--use-case", args.use_case)
        append_optional(cmd, "--style", args.style)
        append_optional(cmd, "--composition", args.composition)
        append_optional(cmd, "--constraints", args.constraints)
    else:
        image_paths = [Path(p).expanduser().resolve() for p in args.image]
        for image in image_paths:
            if not image.exists():
                die(f"input image not found: {image}")
            cmd.extend(["--image", str(image)])
        mask = Path(args.mask).expanduser().resolve() if args.mask else None
        if args.mask_ring:
            if len(image_paths) != 1:
                die("--mask-ring requires exactly one --image")
            mask = out.parent / f"{out.stem}-ring-mask.png"
            make_ring_mask(image_paths[0], mask)
        if mask:
            if not mask.exists():
                die(f"mask not found: {mask}")
            cmd.extend(["--mask", str(mask)])

    if args.force:
        cmd.append("--force")
    if args.dry_run:
        cmd.append("--dry-run")

    env = os.environ.copy()
    if api_key:
        env["OPENAI_API_KEY"] = api_key
    if base_url:
        env["OPENAI_BASE_URL"] = base_url
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(cmd, env=env)


if __name__ == "__main__":
    main()
