# CLI Reference

The `tubesentry` CLI provides commands for running audits, generating synthetic test data, authenticating Pro licenses, and starting the MCP server.

---

## Commands

### `tubesentry demo`
Generates synthetic Google Ads placement data and runs an instant diagnostic pass.

```bash
tubesentry demo [OPTIONS]
```

| Option | Default | Description |
| :--- | :--- | :--- |
| `--out-dir`, `-o` | `./demo_youtube` | Directory to save the generated synthetic CSV |
| `--rows`, `-n` | `25000` | Number of placement rows to generate |
| `--lang`, `-l` | `de` | Formats data with localized headers (`en` or `de`) |

---

### `tubesentry audit`
Audits a real Google Ads or DV360 placement CSV report.

```bash
tubesentry audit <report_csv> [OPTIONS]
```

| Option | Default | Description |
| :--- | :--- | :--- |
| `--lang`, `-l` | `de,en` | Comma-separated target languages for geotargeting validation |
| `--cpa` | `None` | Target CPA to flag performance sinkholes |
| `--key`, `-k` | `None` | TubeSentry Pro license key (or set `TUBESENTRY_API_KEY`) |
| `--out-exclusions` | `None` | Path to export reactive Google Ads Editor exclusions CSV (Pro) |
| `--out-65k` | `None` | Path to export full 65,000-channel shield CSV (Pro) |
| `--html` | `None` | Path to export interactive white-label HTML audit deck (Pro) |
| `--ad-url` | `None` | YouTube ad video URL to profile targeting fit |
| `--ad-text` | `None` | Ad creative brief or copy to profile ICP intent |

---

### `tubesentry mcp`
Launches the FastMCP stdio server.

```bash
tubesentry mcp
```

---

### `tubesentry auth`
Activates TubeSentry Pro using a Polar.sh license key.

```bash
tubesentry auth --key TS_PRO_YOUR_KEY
```
