# BigQuery Data Transfer Service (DTS) Integration

For enterprise marketing engineering and analytics teams, Google Ads provides the native **BigQuery Data Transfer Service (DTS)** to replicate raw placement and campaign metrics into Google Cloud BigQuery.

TubeSentry provides pre-built BigQuery SQL queries and dbt models that analyze raw DTS tables directly inside your data warehouse.

---

## 1. Exporting the BigQuery SQL Model

Export a ready-to-run query for your Google Ads dataset:

```bash
# Standard BigQuery query
tubesentry export bigquery \
  --out tubesentry_audit.sql \
  --dataset google_ads_export \
  --customer-id 1234567890 \
  --days 30

# dbt model format (with partitioning and clustering)
tubesentry export bigquery \
  --out models/tubesentry_placements.sql \
  --dbt
```

---

## 2. Supported Google Ads DTS Tables

The generated SQL reads directly from standard DTS tables:
* `p_Placement_<customer_id>` / `ads_Placement_*`
* `_DATA_DATE` partition pruning for cost efficiency

---

## 3. In-Warehouse Heuristics

The BigQuery macro embeds TubeSentry's risk heuristics directly in BigQuery Standard SQL:
* **Made for Kids:** Regex classification on toddler songs, lullabies, and nursery rhyme tokens.
* **Passive Audio:** Detection of 24/7 lo-fi streams, ambient sleep tracks, and white noise.
* **Underage Sandbox Gaming:** Detection of Roblox, Minecraft, and mobile gaming taps.
* **Foreign Script Geo-Leakage:** Unicode regex matching non-target scripts (`\p{Cyrillic}`, `\p{Arabic}`, `\p{Devanagari}`, `\p{Thai}`, `\p{Han}`).
* **Performance Sinkholes:** Placements exceeding 3x target CPA with 0 conversions.

---

## 4. Output Schema

The query outputs an analytical table partitioned by `audit_date` and clustered by `waste_category`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `audit_date` | `DATE` | Partition date from DTS report |
| `campaign_name` | `STRING` | Google Ads campaign name |
| `channel_id` | `STRING` | 24-character YouTube Channel ID (`UC...`) |
| `channel_title` | `STRING` | Channel display name |
| `formatted_exclusion_url` | `STRING` | Ready-to-exclude string (`youtube.com/channel/UC...`) |
| `waste_category` | `STRING` | Risk classification (`MADE_FOR_KIDS`, `PASSIVE_AUDIO_MUSIC`, etc.) |
| `quality_score` | `FLOAT64` | Quality rating from 1.0 to 10.0 |
| `cost` | `FLOAT64` | Total spend in account currency |
| `wasted_cost` | `FLOAT64` | Spend identified as non-converting waste |
| `impressions` | `INT64` | Total impressions |
| `wasted_impressions` | `INT64` | Waste impressions |

You can schedule this query using BigQuery Scheduled Queries or dbt to automatically populate an exclusion feed or Looker Studio executive dashboard.
