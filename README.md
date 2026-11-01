# TubeSentry 🛡️

**The Agentic-First YouTube & Performance Max Placement Waste Auditor, Creative Targeting Engine & FastMCP Server**

[![CI Tests](https://github.com/flovv/tubesentry/actions/workflows/ci_tests.yml/badge.svg)](https://github.com/flovv/tubesentry/actions/workflows/ci_tests.yml)
[![Docs & GitHub Pages](https://github.com/flovv/tubesentry/actions/workflows/deploy_docs.yml/badge.svg)](https://flovv.github.io/tubesentry/)
[![PyPI version](https://img.shields.io/pypi/v/tubesentry.svg)](https://pypi.org/project/tubesentry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![MCP Server](https://img.shields.io/badge/MCP-FastMCP-purple.svg)](https://modelcontextprotocol.io/)

---

### [📖 Interactive Documentation & Live Guide](https://flovv.github.io/tubesentry/)

---

## 💡 Why TubeSentry?

When running video campaigns on **Google Ads**, **Performance Max (PMax)**, **Demand Gen**, or **DV360**, algorithmic automated placement expansion routinely wastes **20% to 50%+** of advertising spend on low-intent, accidental, or non-human impressions:

* 👶 **Made-for-Kids & Toddler Brainrot:** CoComelon, Baby Shark, nursery rhymes, and toddler sing-alongs streamed on parent iPads (severe bounce rates and COPPA / GDPR-K regulatory risk).
* 🎧 **Passive Background Audio Streams:** 24/7 Lofi beats, sleep music, rain sounds, and meditation loops with zero active visual attention.
* 🎮 **Underage Minor Gaming Drains:** Roblox, Minecraft, Brawl Stars, and Skibidi Toilet mobile livestreams tapped accidentally by young children.
* 🌍 **Foreign Script Geo-Leakage:** Mismatched Cyrillic, Hindi, Arabic, Thai, or Asian broadcast TV channels consuming spend in local EU/US campaigns.
* 🤖 **AI Slop & Content Farms:** Split-screen Subway Surfers + synthetic voiceover shorts and click arbitrage farms with anomalous CTR and zero conversions.
* 🕳️ **Performance Sinkholes:** Placements burning $>3\times$ target CPA with 0 conversions.
* 🎯 **Creative Intent vs. Delivery Reality Gap:** Even clean channels often deliver far outside your creative brief. TubeSentry includes a **Gemini Creative Profiler** to evaluate your ad video URL or brief, extract your Ideal Customer Profile (ICP), and contrast **Expectation vs. Delivery Reality**.

TubeSentry is **100% local-first and privacy-preserving**: your placement CSV reports never leave your machine.

---

## ⚡ Quickstart

### Installation

```bash
pip install tubesentry
```

### 1. Test Drive with 25,000 Synthetic Placements

Generate a realistic 25,000-row Google Ads placement report and run an instant audit diagnostic:

```bash
tubesentry demo --out-dir ./demo_youtube
```

### 2. Audit Your Google Ads / DV360 Placement Report

Export your placement report from Google Ads (*Reports $\rightarrow$ Predefined reports $\rightarrow$ Other $\rightarrow$ Where ads showed $\rightarrow$ Download `.csv`*) or DV360 and run:

```bash
tubesentry audit where_ads_showed.csv --lang de,en --cpa 45.0
```

### 3. Profile Creative Targeting Fit (Gemini Multimodal)

Pass your YouTube Ad URL or creative brief to compare your campaign intent against algorithmic delivery:

```bash
tubesentry audit where_ads_showed.csv \
  --ad-url "https://youtube.com/watch?v=your_ad_video" \
  --ad-text "B2B enterprise cloud security platform for CISOs and DevSecOps teams" \
  --html audit_deck.html
```

---

## 🐍 Python SDK API

TubeSentry seamlessly auto-detects multi-language CSV exports (**English, German, Spanish, French, Italian, Dutch**):

```python
import tubesentry as ts

# Run instant placement audit
report = ts.audit_placements(
    report="where_ads_showed.csv",
    target_languages=["de", "en"],
    target_cpa=40.0,
    ad_url="https://youtube.com/watch?v=demo_video",
    ad_text="Enterprise Kubernetes automation for DevOps and SRE teams.",
)

print(f"Audited Spend:   €{report.total_spend:,.2f}")
print(f"Wasted Spend:    €{report.total_wasted_spend:,.2f} ({report.wasted_spend_percentage:.1f}%)")
print(f"Quality Score:   {report.weighted_quality_score:.1f} / 10.0")

if report.creative_alignment:
    print(f"Targeting Fit:   {report.creative_alignment.overall_alignment_score:.1f} / 10.0")
    print(f"Off-Target Bleed: €{report.creative_alignment.off_target_spend:,.2f}")
```

---

## 🤖 Claude Desktop, Claude Code & Cursor MCP Server

TubeSentry includes a native **Model Context Protocol (FastMCP)** server. AI coding assistants and chat environments can audit placements and inspect channels directly in natural language.

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tubesentry": {
      "command": "tubesentry-mcp"
    }
  }
}
```

Or run without installation via `uvx`:

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

### Cursor IDE Configuration

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "tubesentry": {
      "command": "tubesentry-mcp"
    }
  }
}
```

### Example Natural Language Prompts
* *"Audit my Google Ads placement report at `~/Downloads/pmax_october.csv` for toddler brainrot and passive music streams."*
* *"Profile this YouTube video ad URL with Gemini: `https://youtube.com/watch?v=...` and tell me what contextual topics and negative exclusions to set in Google Ads."*
* *"Inspect these 5 YouTube channels for COPPA and background audio risk: `UCbCmjCuTUZos6Inko4u57UQ`, `UCSJ4gkVC6NrvII8umztf0Ow`."*

---

## 📊 Open-Core vs. TubeSentry Pro

| Feature | Open-Core `tubesentry` (Free) | `tubesentry_pro` (Licensed) |
| :--- | :---: | :---: |
| **Exact Category Spend & % Waste Breakdown** | ✅ Full Visibility | ✅ Full Visibility |
| **Impression-Weighted Quality Score (1–10)** | ✅ Included | ✅ Included |
| **Top 25 Worst Offender Channels** | ✅ Unmasked | ✅ Unmasked |
| **Tail Offender Channels ($c_{26} \dots c_M$)** | 🔒 Masked (`UC••••••••••••`) | ✅ 100% Unmasked |
| **Bundled Waste Seed Dictionary** | 2,500 Notorious Channels | **250,000 Pre-Classified Registry** |
| **Long-Tail Unknown Channel Enrichment** | Regex Heuristics | **Async 50-ID Batch YouTube API v3 Resolver** |
| **Google Ads 65,000 Exclusion Shield CSV** | ❌ | ✅ 1-Click Ready (`google_ads_65k_full_shield.csv`) |
| **DV360 SDF Exclusion Chunks** | ❌ | ✅ 10,000-Row SDF Blocks |
| **Gemini Creative Targeting Fit Engine** | ✅ Core Matching | ✅ Multimodal Deep Profiler |
| **CFO / Client Brand-Safety HTML Audit Deck** | ❌ | ✅ White-Label Interactive Chart.js Deck |

---

## 🔑 Activating TubeSentry Pro

Obtain an instant Single Audit Pass (€199) or Agency Unlimited Key at [tubesentry.dev](https://tubesentry.dev):

```bash
tubesentry auth --key TS_PRO_YOUR_POLAR_KEY
```

Or via Python:

```python
import tubesentry as ts
ts.install_pro(api_key="TS_PRO_...")
```

---

## 🛡️ Privacy & Security Guarantee

* **Local-First:** All CSV ingestion, regex scoring, and database lookups run 100% locally on your machine.
* **Zero Cloud Ingestion:** Your clients' placement data, budgets, and impressions are never uploaded to any third-party server.
* **Serverless Architecture:** 0€ infrastructure overhead.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
