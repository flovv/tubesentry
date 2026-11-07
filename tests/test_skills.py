from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from tubesentry.cli import app
from tubesentry.mcp_server import get_audit_skill_guide
from tubesentry.skills import (
    get_bundled_skill_path,
    get_bundled_skill_text,
    install_skill,
)

runner = CliRunner()


def test_get_bundled_skill_path() -> None:
    p = get_bundled_skill_path()
    assert p.exists()
    assert p.name == "SKILL.md"


def test_get_bundled_skill_text() -> None:
    text = get_bundled_skill_text()
    assert "name: youtube-placement-audit" in text
    assert "YouTube Placement Audit Skill" in text
    assert "tubesentry audit" in text


def test_install_skill_custom_dir(tmp_path: Path) -> None:
    dest = install_skill(target_dir=tmp_path)
    assert dest.exists()
    assert dest.name == "SKILL.md"
    assert "youtube-placement-audit" in str(dest.parent)
    assert dest.read_text(encoding="utf-8") == get_bundled_skill_text()


def test_cli_skill_commands(tmp_path: Path) -> None:
    # 1. Help
    res_help = runner.invoke(app, ["skill", "--help"])
    assert res_help.exit_code == 0
    assert "install" in res_help.output
    assert "show" in res_help.output
    assert "path" in res_help.output

    # 2. Path
    res_path = runner.invoke(app, ["skill", "path"])
    assert res_path.exit_code == 0
    assert "SKILL.md" in res_path.output

    # 3. Show
    res_show = runner.invoke(app, ["skill", "show"])
    assert res_show.exit_code == 0
    assert "name: youtube-placement-audit" in res_show.output

    # 4. Install
    out_dir = tmp_path / "skills_test"
    res_inst = runner.invoke(app, ["skill", "install", "--target-dir", str(out_dir)])
    assert res_inst.exit_code == 0
    assert "installed to" in res_inst.output
    assert (out_dir / "youtube-placement-audit" / "SKILL.md").exists()


def test_mcp_get_audit_skill_guide() -> None:
    guide = get_audit_skill_guide()
    assert isinstance(guide, str)
    assert "name: youtube-placement-audit" in guide
