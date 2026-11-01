# TubeSentry Pro Commercial Edition

**TubeSentry Pro** provides deep intelligence for performance marketing agencies, CMOs, and enterprise brand safety teams.

---

## Pro Features Overview

### 1. 250,000-Channel Pre-Classified Intelligence Registry
Open-core includes a bundled 2,500 seed channel database. Pro unlocks an embedded PyArrow/Parquet database containing **250,000 pre-scored YouTube channels**, enabling sub-millisecond local classification without consuming YouTube API quota.

### 2. Async 50-ID Batch YouTube Data API v3 Enricher
For unrecognized long-tail channels, Pro uses an asynchronous batch enricher to fetch metadata (topics, languages, audience tags, avatar thumbnails) in 50-ID chunks with an embedded SQLite cache.

### 3. Google Ads 65,000 Exclusion Shield
Google Ads enforces a strict hard limit of 65,000 placement exclusions at the account/MCC level. TubeSentry Pro quantizes its 250,000-channel registry to output a formatted `google_ads_65k_full_shield.csv` ready for 1-click import into Google Ads Editor.

### 4. Interactive CFO / Client HTML Pitch Deck
Compiles a standalone, single-file interactive presentation deck containing:
* Executive KPI cards (Quality index, COPPA toddler exposure, 12-month run-rate recovery).
* Chart.js interactive visualizations.
* "Wall of Shame" visual thumbnail spotlights.
* Creative Intent vs. Delivery Reality fit audit cards.

---

## Licensing & Activation

Visit [tubesentry.dev](https://tubesentry.dev) to obtain a license:
* **Single Audit Pass:** €199 (unmasks all channels for a single campaign).
* **Agency Monthly:** €499/mo (unlimited unmasked audits, white-label decks, and automated exclusion shields).

```bash
tubesentry auth --key TS_PRO_YOUR_POLAR_KEY
```
