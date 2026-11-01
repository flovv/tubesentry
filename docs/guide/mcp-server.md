# Model Context Protocol (FastMCP) Server

TubeSentry provides native MCP support, enabling AI models in **Claude Desktop**, **Claude Code**, and **Cursor** to audit ad placements and inspect YouTube channels natively.

---

## Configuration

### Claude Desktop

Edit your `claude_desktop_config.json`:
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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

### Cursor IDE

Create or update `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "tubesentry": {
      "command": "tubesentry-mcp"
    }
  }
}
```

---

## Exposed MCP Tools

### 1. `audit_placement_report`
Audits a Google Ads or DV360 placement CSV export for waste categories.
* **Arguments:** `csv_path` (required), `target_languages`, `target_cpa`, `ad_url`, `ad_text`, `output_dir`.
* **Output:** Full audit summary including waste breakdown, quality score, top offenders, and creative alignment metrics.

### 2. `inspect_youtube_channels`
Looks up specific YouTube Channel IDs or URLs in the TubeSentry Intelligence Database.
* **Arguments:** `channel_ids_or_urls` (list of strings).
* **Output:** Channel title, waste category, confidence, and audit rationale.

### 3. `profile_creative_intent`
Profiles a YouTube ad URL or brief with Gemini.
* **Arguments:** `ad_url`, `ad_text`.
* **Output:** Target persona, recommended contextual topic entities, and negative anti-personas.

---

## Example Natural Language Workflows

```text
User: "Audit ~/Downloads/pmax_october.csv for Made-for-Kids toddler channels and export the exclusion list to ~/Desktop/exclusions.csv"

Claude: Calling tubesentry.audit_placement_report(csv_path="~/Downloads/pmax_october.csv", output_dir="~/Desktop")
...
Audit complete! 38.4% of your spend (€14,200) was wasted on toddler and passive music channels. 
Exclusion file saved to ~/Desktop/google_ads_reactive_exclusions.csv.
```
