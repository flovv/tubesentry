from __future__ import annotations

import pandas as pd
import pytest

from tubesentry import audit_placements
from tubesentry.contracts.schemas import AuditSummaryReport


def test_free_tier_masking_invariant(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure Pro is treated as inactive / no license key passed
    monkeypatch.delenv("TUBESENTRY_API_KEY", raising=False)

    # Build synthetic dataframe with 500 distinct waste channels
    rows = []
    total_expected_waste = 0.0

    for i in range(500):
        # Channel IDs matching toddler or seed patterns
        ch_id = f"UC{str(i).zfill(22)}"
        cost = round(10.0 + (500 - i) * 0.5, 2)  # descending cost
        total_expected_waste += cost
        rows.append(
            {
                "raw_placement": f"youtube.com/channel/{ch_id}",
                "channel_id": ch_id,
                "handle_or_video_id": None,
                "channel_title": f"Nursery Rhymes Toddler Kids #{i + 1}",
                "placement_type": "YouTube channel",
                "impressions": 1000,
                "views": 200,
                "clicks": 15,
                "cost": cost,
                "conversions": 0.0,
                "currency_code": "EUR",
            }
        )

    # Add 100 clean channels as well
    for j in range(100):
        rows.append(
            {
                "raw_placement": f"youtube.com/channel/UCCLEAN_{str(j).zfill(15)}",
                "channel_id": f"UCCLEAN_{str(j).zfill(15)}",
                "handle_or_video_id": None,
                "channel_title": f"Technology Engineering Education #{j + 1}",
                "placement_type": "YouTube channel",
                "impressions": 500,
                "views": 250,
                "clicks": 10,
                "cost": 50.0,
                "conversions": 2.0,
                "currency_code": "EUR",
            }
        )

    df = pd.DataFrame(rows)
    total_spend = df["cost"].sum()

    report: AuditSummaryReport = audit_placements(
        report=df,
        target_languages=["de", "en"],
        print_banner=False,
    )

    assert report.is_pro_audit is False
    assert round(report.total_spend, 2) == round(total_spend, 2)
    assert round(report.total_wasted_spend, 2) == round(total_expected_waste, 2)
    assert report.total_waste_channels == 500

    # Top 25 unmasked, remaining 475 masked
    unmasked = [c for c in report.top_offenders if not c.is_masked]
    masked = [c for c in report.top_offenders if c.is_masked]

    assert len(unmasked) == 25
    assert len(masked) == 475
    assert report.masked_offenders_count == 475

    # Check unmasked channels retain true ID and title
    for rec in unmasked:
        assert rec.channel_id.startswith("UC")
        assert "••••" not in rec.channel_id
        assert "[LOCKED IN FREE TIER" not in rec.channel_title

    # Check masked channels have locked placeholder
    for rec in masked:
        assert rec.channel_id == "UC••••••••••••"
        assert rec.channel_title == "[LOCKED IN FREE TIER — Upgrade to TubeSentry Pro]"
