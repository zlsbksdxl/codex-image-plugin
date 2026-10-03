from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/codex-image-plugin"


def test_plugin_manifest_and_skill_exist() -> None:
    manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "codex-image-plugin"
    assert manifest["skills"] == "./skills/"
    assert (PLUGIN / "skills/codex-image-plugin/SKILL.md").is_file()
    assert (PLUGIN / "skills/codex-image-plugin/agents/openai.yaml").is_file()
    assert (PLUGIN / "skills/codex-image-plugin/scripts/image.py").is_file()


def test_documentation_has_both_languages() -> None:
    assert "# Codex Image Plugin" in (ROOT / "README.md").read_text()
    assert "# Codex Image Plugin" in (ROOT / "README.zh-CN.md").read_text()
