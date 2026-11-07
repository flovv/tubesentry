# TubeSentry Agent Skill (`youtube-placement-audit`)

TubeSentry includes an installable Agent Skill compliant with modern coding assistant formats (Antigravity, Claude Code, Cursor, Codex).

The skill gives autonomous AI agents step-by-step decision rules, tool calling recipes, data contracts, and operational best practices for auditing YouTube and Performance Max placement reports.

---

## Installing the Skill

### 1. Via skills.sh / npx (Universal Agent Installer)

Install directly to Claude Code, Cursor, Copilot, or Antigravity via the open `skills` ecosystem:

```bash
npx skills add flovv/tubesentry
```

### 2. Via TubeSentry CLI

Run the CLI command in any workspace root:

```bash
tubesentry skill install
```

Or without installing Python packages locally:

```bash
uvx --from tubesentry tubesentry skill install
```

The installer automatically detects the workspace environment:
1. `./.agents/skills/` (Antigravity / Hermes standard)
2. `./.claude/skills/` (Claude Code standard)
3. Custom location via `--target-dir <path>`

---

## Inspecting the Skill Content

You can print the full skill guide directly to the terminal:

```bash
tubesentry skill show
```

Or query the local filesystem path of the bundled markdown file:

```bash
tubesentry skill path
```

---

## MCP Server Integration

Agents connected via the FastMCP server can also query the skill instructions dynamically via the `get_audit_skill_guide` tool:

```python
from tubesentry.mcp_server import get_audit_skill_guide

guide = get_audit_skill_guide()
```

---

## What the Skill Teaches the Agent

* **Division of Responsibilities:** Never write ad-hoc regex parsing or manual CSV loops; always use `audit_placements()` and native quantizers.
* **Metric Hierarchy:** Prioritize impression-weighted quality scores over raw channel counts (e.g. 10 toddler channels burning 45% of impressions).
* **Creative Alignment:** How to contrast multimodal Gemini ICP targeting intent with actual algorithmic delivery.
* **Google Ads Constraints:** Applying the 65,000-channel exclusion limit correctly via Google Ads Editor shields.
