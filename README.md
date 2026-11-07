# TubeSentry

Local-first placement auditor and Model Context Protocol (MCP) server for Google Ads and DV360.

[![CI Tests](https://github.com/flovv/tubesentry/actions/workflows/ci_tests.yml/badge.svg)](https://github.com/flovv/tubesentry/actions/workflows/ci_tests.yml)
[![Documentation](https://github.com/flovv/tubesentry/actions/workflows/deploy_docs.yml/badge.svg)](https://flovv.github.io/tubesentry/)
[![PyPI version](https://img.shields.io/pypi/v/tubesentry.svg)](https://pypi.org/project/tubesentry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)

**Documentation:** [https://flovv.github.io/tubesentry/](https://flovv.github.io/tubesentry/)

---

## Description

TubeSentry analyzes placement reports ("Where ads showed") from Google Ads (YouTube, Performance Max, Demand Gen) and Google Display & Video 360 (DV360). It categorizes placements against known risk patterns, quantifies wasted media spend, calculates an impression-weighted quality score, and generates exclusion lists for Google Ads Editor.

Processing runs 100% locally. Client placement data, impressions, and budgets never leave your machine.

**Tags:** `google-ads`, `youtube-ads`, `performance-max`, `dv360`, `adtech`, `ppc`, `mcp-server`, `placement-exclusions`, `marketing-analytics`

---

## What TubeSentry Detects

When running YouTube or Performance Max campaigns, broad placement algorithms frequently allocate budget to non-converting or unintended inventory:

* **Made for Kids (MFK):** Toddler songs and children's cartoons streamed on shared mobile devices, leading to accidental taps and COPPA compliance concerns.
* **Passive Audio & Music:** 24/7 background lo-fi streams, ambient sleep tracks, and white-noise loops where visual engagement is minimal.
* **Underage Gaming:** Channels dedicated to mobile sandbox titles (Roblox, Minecraft) that generate high view counts with negligible conversion value.
* **Foreign Script Delivery:** Placements running on non-target language scripts (Cyrillic, Devanagari, Arabic, Thai) within domestic campaigns.
* **Low-Quality Content Farms:** Automated short-form compilations designed for view arbitrage with high bounce rates.
* **Performance Sinkholes:** Placements that exceed 3x target CPA without registering conversions.
* **Creative Alignment Gap:** Optional analysis comparing your creative's intended target audience with the actual channels where impressions ran.

---

## Installation

```bash
pip install tubesentry
```

Or run directly without installation using `uvx`:

```bash
uvx --from tubesentry tubesentry --help
```

---

## Quickstart

### 1. Run a Synthetic Demo Audit

Generate a 25,000-row synthetic placement report and review the audit output:

```bash
tubesentry demo --out-dir ./demo_output
```

### 2. Audit an Exported Placement CSV

Export your placement report from Google Ads (*Reports > Predefined reports > Other > Where ads showed > Download CSV*) or DV360:

```bash
tubesentry audit where_ads_showed.csv --lang en,de --cpa 45.0
```

### 3. Compare Creative Intent to Actual Delivery

Pass your YouTube ad URL or creative brief text to compare target audience expectations against delivery reality:

```bash
tubesentry audit where_ads_showed.csv \
  --ad-url "https://youtube.com/watch?v=your_ad_id" \
  --ad-text "B2B infrastructure platform for DevOps and cloud architects"
```

---

## Python API

TubeSentry supports localized Google Ads CSV exports (English, German, Spanish, French, Italian, Dutch):

```python
import tubesentry as ts

report = ts.audit_placements(
    report="where_ads_showed.csv",
    target_languages=["en", "de"],
    target_cpa=40.0,
    ad_url="https://youtube.com/watch?v=your_ad_id",
    ad_text="B2B cloud infrastructure monitoring for SRE teams.",
)

print(f"Audited Spend:    EUR {report.total_spend:,.2f}")
print(f"Wasted Spend:     EUR {report.total_wasted_spend:,.2f} ({report.wasted_spend_percentage:.1f}%)")
print(f"Quality Score:    {report.weighted_quality_score:.1f} / 10.0")

if report.creative_alignment:
    print(f"Alignment Score:  {report.creative_alignment.overall_alignment_score:.1f} / 10.0")
    print(f"Off-Target Spend: EUR {report.creative_alignment.off_target_spend:,.2f}")
```

---

## MCP Server (Claude Desktop, Claude Code, Cursor)

TubeSentry includes a native Model Context Protocol (FastMCP) server, allowing AI coding assistants and agents to inspect placements and channels directly.

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tubesentry": {
      "command": "uvx",
      "args": ["--from", "tubesentry", "tubesentry-mcp"]
    }
  }
}
```

### Cursor Configuration

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "tubesentry": {
      "command": "uvx",
      "args": ["--from", "tubesentry", "tubesentry-mcp"]
    }
  }
}
```

---

## Agent Skill

TubeSentry includes an installable skill (`youtube-placement-audit`) formatted with standard frontmatter for AI coding assistants and agent environments (Antigravity, Claude Code, Cursor, Codex).

### Install Skill into Current Workspace

```bash
tubesentry skill install
```

Or run without installation via `uvx`:

```bash
uvx --from tubesentry tubesentry skill install
```

This places `SKILL.md` into `.agents/skills/youtube-placement-audit/` (or `.claude/skills/`), providing autonomous agents with:
* Operational recipes for analyzing Google Ads / DV360 placement reports
* Waste category decision rules and CPA thresholds
* FastMCP tool invocation patterns and creative targeting fit guides

To view the raw skill instructions directly in the terminal:

```bash
tubesentry skill show
```

---

## Editions

| Feature | Open-Core (Free) | Pro (Licensed) |
| :--- | :--- | :--- |
| Waste category breakdown and percentage | Yes | Yes |
| Impression-weighted quality score (1-10) | Yes | Yes |
| Worst-offender channel reporting | Top 25 unmasked | All unmasked |
| Bundled waste seed database | 2,500 channels | 250,000-channel registry |
| Channel metadata resolution | Local heuristics | 50-ID batch YouTube API v3 enricher |
| Google Ads 65,000 exclusion shield CSV | No | Yes (`google_ads_65k_full_shield.csv`) |
| DV360 SDF exclusion chunks | No | Yes (10,000-row SDF blocks) |
| Creative targeting fit engine | Core matching | Multimodal creative profiler |
| Client HTML presentation deck | No | Yes (single-file HTML report) |

---

## Pro Activation

Single audit passes and agency licenses are available via [Polar](https://buy.polar.sh/polar_cl_lRuifr3uJS0LR0k6frhg3JEKBRZNQq75hv7cS2am9cX).

Activate via CLI:

```bash
tubesentry auth --key TS_PRO_YOUR_POLAR_KEY
```

Or via Python:

```python
import tubesentry as ts

ts.install_pro(api_key="TS_PRO_...")
```

---

## Security & Privacy

* **Local execution:** All CSV parsing, heuristic scoring, and database lookups run locally.
* **No cloud ingestion:** Client spend numbers, impressions, and account identifiers are never transmitted to external servers.
* **No telemetry:** The core package does not collect analytics or track usage.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
