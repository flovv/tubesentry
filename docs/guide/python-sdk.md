# Python SDK API

TubeSentry is fully importable as a Python library.

---

## Core Function: `audit_placements`

```python
from tubesentry import audit_placements

report = audit_placements(
    report="where_ads_showed.csv",       # Path, string, or pandas DataFrame
    target_languages=["de", "en"],       # Approved target languages
    target_cpa=35.0,                     # Target CPA in account currency
    api_key="TS_PRO_...",               # Optional TubeSentry Pro license key
    ad_url="https://youtube.com/...",    # Optional ad URL for creative fit
    ad_text="...",                       # Optional ad copy / creative brief
    export_exclusions_csv="exc.csv",     # Export reactive exclusions
    export_65k_shield_csv="65k.csv",     # Export 65,000-channel shield
    export_html_deck="deck.html",        # Export HTML CFO report
)
```

### Return Value: `AuditSummaryReport`

* `total_placements_audited: int`
* `total_spend: float`
* `total_wasted_spend: float`
* `wasted_spend_percentage: float`
* `weighted_quality_score: float` (1.0 to 10.0 scale)
* `category_breakdowns: dict[str, WasteCategoryBreakdown]`
* `top_offenders: list[ClassifiedChannelRecord]`
* `creative_alignment: CreativeAlignmentSummary | None`

---

## Utility Functions

```python
from tubesentry.io.ingestor import load_and_standardize_csv, sample_by_impressions

# Load and normalize headers across English, German, Spanish, French, etc.
df = load_and_standardize_csv("placement_report.csv")

# Statistically sample large datasets proportional to impression weight
sample_df = sample_by_impressions(df, n=1000)
```
