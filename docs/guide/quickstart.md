# Quickstart Guide

Get up and running with **TubeSentry** in under 60 seconds.

## Installation

Install via pip:

```bash
pip install tubesentry
```

Or install with all development tooling:

```bash
pip install "tubesentry[dev]"
```

## 1. Instant Test Drive with Synthetic Placements

Generate a realistic 25,000-placement synthetic campaign report and run an instant audit diagnostic:

```bash
tubesentry demo --out-dir ./demo_youtube --rows 25000 --lang en
```

Output highlights:
* Total spend audited vs. wasted spend total
* Impression-weighted quality score (1.0 to 10.0 scale)
* Top offending channels unmasked
* Category-by-category breakdown

## 2. Auditing Real Google Ads / DV360 Reports

### Exporting from Google Ads:
1. Log into Google Ads.
2. Navigate to **Reports** $\rightarrow$ **Predefined reports (Dimensions)** $\rightarrow$ **Other** $\rightarrow$ **Where ads showed**.
3. Set your date range (e.g. Last 30 Days or All Time).
4. Click **Download** $\rightarrow$ `.csv`.

### Running the Audit:
```bash
tubesentry audit where_ads_showed.csv --lang de,en --cpa 45.0
```

### Pro Tip: Adding Ad Creative Targeting Verification:
```bash
tubesentry audit where_ads_showed.csv \
  --ad-url "https://youtube.com/watch?v=..." \
  --ad-text "Enterprise Kubernetes multi-cloud management for DevOps teams" \
  --html cfo_audit_deck.html
```
