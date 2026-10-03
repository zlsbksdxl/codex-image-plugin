from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/gpt-image-2-codex"


def test_plugin_manifest_and_skill_exist() -> None:
    manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "gpt-image-2-codex"
    assert manifest["skills"] == "./skills/"
    assert (PLUGIN / "skills/gpt-image-2/SKILL.md").is_file()
    assert (PLUGIN / "skills/gpt-image-2/agents/openai.yaml").is_file()
    assert (PLUGIN / "skills/gpt-image-2/scripts/image.py").is_file()


def test_documentation_has_both_languages() -> None:
    assert "# GPT Image 2 for Codex" in (ROOT / "README.md").read_text()
    assert "# Codex 的 GPT Image 2 插件" in (ROOT / "README.zh-CN.md").read_text()
