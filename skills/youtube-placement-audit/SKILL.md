---
name: youtube-placement-audit
description: Audit, score, and eliminate wasted ad spend in Google Ads and DV360 YouTube placement reports using tubesentry and tubesentry-pro.
version: 0.1.0
author: flovv
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [youtube, google-ads, dv360, pmax, placement-audit, brand-safety, coppa, exclusions, mcp-server]
    related_skills: []
---

# YouTube Placement Audit Skill (`youtube-placement-audit`)

Audits, scores, and eliminates wasted ad budget from Google Ads and DV360 YouTube and Performance Max (PMax) placement reports:
- **`tubesentry` (Open-Core):** Automated ingestion of multilingual Google Ads / DV360 CSV placement exports, 6-vector heuristic waste detection (Made-for-Kids toddler content, passive audio/sleep music, underage gaming, foreign script leakage, low-quality content farms, performance sinkholes), bundled 2,500-channel seed database, Top 25 unmasked diagnostic reporting, and FastMCP Server for Claude Desktop, Cursor, and AI agents.
- **`tubesentry-pro` (Commercial):** 250,000-channel pre-classified intelligence registry (PyArrow zstd Parquet), asynchronous 50-ID batch YouTube Data API v3 enricher with local SQLite cache, Google Ads 65,000-channel exclusion shield quantizer (`google_ads_65k_full_shield.csv`), interactive CFO / Client HTML pitch deck with visual proof cards, Wikipedia Knowledge Graph topic entity breakdowns, and impression-weighted quality scoring (1–10).

> [!IMPORTANT]
> **Division of Responsibilities:**
> * **The Engine (`tubesentry` / `tubesentry_pro`) executes all data processing:** Never write custom CSV parsing loops, manual regexes, or custom YouTube API batching. Always invoke `audit_placements()`, `run_free_audit()`, or the CLI/MCP tools.
> * **The Agent formats inputs and guides decisions:** Identify placement report columns, inspect flag rationales, check language/geotargeting alignment, review the visual evidence, and guide media buyers on deploying the 65k exclusion shield into Google Ads Editor.
> * **Exclusion vs. Bidding Distinction:** YouTube placement exclusions actively prevent ads from serving on flagged channels. Placement exclusions applied at the campaign or account level are hard blocks enforced by Google's ad server.

---

## Pro Licensing & Availability

Check whether Pro is available:
```python
import tubesentry
is_pro = tubesentry.is_pro_available()
```

Pro requires a Polar license key or test key:
- **Environment Variable:** `os.environ["TUBESENTRY_API_KEY"] = "TS_PRO_..."`
- **Parameter:** Pass `api_key="TS_PRO_..."` directly into `audit_placements()`.
- **Local Dev / CI Bypass:** Set `os.environ["TUBESENTRY_MOCK_AUTH"] = "1"` or use a test key prefixed with `TS_TEST_`.

---

## Quick Reference: CLI Commands

| Task | Command |
| :--- | :--- |
| **Run Placement Audit** | `tubesentry audit <report.csv> [--cpa 15.0] [--export-script cleanup.js] [--html report.html] [--ad-url <url>]` |
| **Export Google Ads Script** | `tubesentry export script --report <report.csv> --out cleanup.js [--dry-run/--live]` |
| **Export BigQuery SQL** | `tubesentry export bigquery --out audit.sql [--dataset <name>] [--dbt]` |
| **Generate Demo Data** | `tubesentry demo --out-dir demo --rows 500` |
| **Start FastMCP Server** | `tubesentry mcp` |
| **Install Agent Skill** | `tubesentry skill install [--target-dir .agents/skills]` |
| **Show Skill Guide** | `tubesentry skill show` |
| **Authenticate Pro** | `tubesentry auth --key <TS_PRO_...>` |

---

## Creative Targeting Fit Engine (Gemini Profiler)

Given an ad creative URL or brief, TubeSentry invokes Gemini to infer:
1. Ideal Customer Profile (ICP) & decision-maker roles.
2. Recommended contextual topic entities (Wikipedia / Knowledge Graph).
3. Negative anti-personas (Made-for-Kids, underage gaming, passive audio, content farms).
4. Correlates intent against actual placement delivery to compute the **Targeting Alignment Score (1–10)**, on-target vs. off-target spend, and side-by-side **Expectation vs. Reality** comparison cards in the HTML report.

```python
from tubesentry import audit_placements

report = audit_placements(
    report="campaign_placements.csv",
    api_key="TS_PRO_KEY",
    export_html_deck="cfo_audit_deck.html",
    ad_url="https://youtube.com/watch?v=...",
    ad_text="Enterprise Kubernetes orchestration and cloud cost optimization platform for DevOps teams.",
)

print(f"Alignment Score: {report.creative_alignment.overall_alignment_score} / 10")
print(f"Off-Target Bleed: EUR {report.creative_alignment.off_target_spend:,.2f} ({report.creative_alignment.off_target_percentage}%)")
```

---

## FastMCP Server Integration

`tubesentry` includes a native FastMCP server (`tubesentry.mcp_server`) exposing placement auditing tools directly to Claude Desktop, Cursor, and AI agents.

### Claude Desktop Configuration (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "tubesentry": {
      "command": "uvx",
      "args": ["--from", "tubesentry", "tubesentry-mcp"],
      "env": {
        "TUBESENTRY_API_KEY": "TS_PRO_..."
      }
    }
  }
}
```

### Available MCP Tools

1. **`audit_placement_report(csv_path, target_languages, target_cpa, api_key, output_dir, ad_url, ad_text, gemini_api_key)`**:
   Audits a Google Ads or DV360 placement CSV report. When Pro is active or `api_key` is provided, automatically outputs:
   - `google_ads_reactive_exclusions.csv` (all flagged placements in the campaign)
   - `google_ads_65k_full_shield.csv` (quantized 65k account-level exclusion shield)
   - `youtube_waste_audit.html` (interactive CFO presentation deck)
2. **`inspect_youtube_channels(channel_ids_or_urls, target_languages, api_key)`**:
   Queries individual channel IDs or URLs against the Seed DB, 250k Pro Registry, and heuristics. Returns waste category, confidence, and detection source.
3. **`profile_creative_intent(ad_url, ad_text, gemini_api_key)`**:
   Extracts target ICP, recommended contextual topics, and anti-personas from video URL or text brief.
4. **`activate_tubesentry_pro(api_key)`**:
   Validates license key against Polar and activates Pro.

---

## Essential Code Recipes

### Recipe 1: Run Placement Audit & Export Exclusions
```python
import tubesentry

report = tubesentry.audit_placements(
    report="google_ads_placements.csv",
    target_languages=["de", "en"],
    target_cpa=25.0,
    api_key="TS_PRO_...",
    export_exclusions_csv="output/reactive_exclusions.csv",
    export_65k_shield_csv="output/shield_65k.csv",
    export_html_deck="output/deck.html",
)

print(f"Audited Spend: EUR {report.total_spend:,.2f}")
print(f"Wasted Spend:  EUR {report.total_wasted_spend:,.2f} ({report.wasted_spend_percentage:.1f}%)")
print(f"Quality Score: {report.weighted_quality_score:.1f} / 10.0")
print(f"Exclusions generated: {len(report.top_offenders):,} channels")
```

### Recipe 2: Inspect Specific Channels in Agent Conversations
```python
from tubesentry.mcp_server import inspect_youtube_channels

results = inspect_youtube_channels([
    "UCbCmjCuTUZos6Inko4u57UQ",  # Cocomelon
    "https://www.youtube.com/channel/UCSJ4gkVC6NrvII8umztf0Ow",  # Lofi Girl
    "https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ",  # MKBHD (Clean)
])

for r in results:
    print(f"[{r['waste_category']}] {r['channel_title']} (Confidence: {r['waste_confidence']:.2f})")
    print(f"  Reason: {r['reason_summary']}")
```

### Recipe 3: Statistical Proportional Sampling for Huge CSVs
For reports with 20,000+ placements under API limits, sample proportional to impression volume:
```python
from tubesentry.io.ingestor import load_placement_report, sample_by_impressions

df = load_placement_report("massive_placements_report.csv")
sample_df = sample_by_impressions(df, n=500)
```

### Recipe 4: Generate Copy-Paste Google Ads Exclusion Script
Output a complete `.js` file for Google Ads Scripts to automate account-level exclusions:
```python
from tubesentry import generate_google_ads_script

channels = ["UCbCmjCuTUZos6Inko4u57UQ", "UCSJ4gkVC6NrvII8umztf0Ow"]
script_js = generate_google_ads_script(
    channel_ids_or_urls=channels,
    dry_run=True,
    shared_list_name="TubeSentry Waste Shield",
)
```

### Recipe 5: BigQuery DTS SQL Macro for Enterprise Warehouses
Generate an audit query to run directly on Google Ads BigQuery Data Transfer Service tables:
```python
from tubesentry import generate_bigquery_dts_sql

sql = generate_bigquery_dts_sql(dataset="google_ads_export", lookback_days=30, as_dbt=True)
```

---

## Best Practices & Decision Rules

1. **Impression-Weighted Loss over Raw Channel Count:**  
   Never report waste solely as "X% of channels." A handful of toddler channels can consume 40%+ of impressions. Always report **Impression Waste Impact** and **Placement Quality Index**.
2. **Toddler Tap Waste (<10) vs. Adult Content:**  
   Treat toddler content (`is_young_kids == True`) as high-urgency waste. Toddlers accidentally tap screens, causing near-100% bounce rates and COPPA compliance risk.
3. **Passive Music & Audio Streams:**  
   Flag lo-fi, sleep music, and 10-hour ambient streams as zero-attention placements unless the campaign is explicitly audio-first.
4. **Google Ads 65,000 Exclusion Limit:**  
   Google Ads limits account-level exclusion lists to 65,000 items. When generating account shields, `tubesentry_pro` quantizes the 250,000 registry into the top 65,000 highest-risk channels.
5. **Language Alignment Validation:**  
   Always inspect campaign target languages. A Spanish channel is waste leakage on a German domestic campaign, but completely legitimate on a LATAM campaign. Use `target_languages` appropriately.
