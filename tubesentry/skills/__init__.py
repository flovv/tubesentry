from __future__ import annotations

from importlib import resources
from pathlib import Path


def get_bundled_skill_path() -> Path:
    """Returns the local filesystem path to the bundled SKILL.md file."""
    ref = resources.files("tubesentry.skills.youtube_placement_audit").joinpath("SKILL.md")
    return Path(str(ref))


def get_bundled_skill_text() -> str:
    """Returns the full markdown content of the bundled Agent Skill."""
    ref = resources.files("tubesentry.skills.youtube_placement_audit").joinpath("SKILL.md")
    return ref.read_text(encoding="utf-8")


def install_skill(target_dir: Path | str | None = None) -> Path:
    """Installs the TubeSentry AI agent skill into the target workspace directory.

    If target_dir is None, auto-detects:
      1. ./.agents/skills (Antigravity standard)
      2. ./.claude/skills (Claude Code standard)
      3. Default fallback: ./.agents/skills
    """
    if target_dir is None:
        cwd = Path.cwd()
        if (cwd / ".agents" / "skills").exists():
            dest_root = cwd / ".agents" / "skills"
        elif (cwd / ".claude" / "skills").exists():
            dest_root = cwd / ".claude" / "skills"
        else:
            dest_root = cwd / ".agents" / "skills"
    else:
        dest_root = Path(target_dir)

    skill_dest_dir = dest_root / "youtube-placement-audit"
    skill_dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = skill_dest_dir / "SKILL.md"

    content = get_bundled_skill_text()
    dest_file.write_text(content, encoding="utf-8")
    return dest_file


__all__ = [
    "get_bundled_skill_path",
    "get_bundled_skill_text",
    "install_skill",
]
