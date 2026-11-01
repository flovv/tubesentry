from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from tubesentry.core.auditor import normalize_topic_category, run_free_audit
from tubesentry.core.heuristics import (
    evaluate_heuristics_detailed,
    is_young_kids_text,
)
from tubesentry.io.ingestor import sample_by_impressions


def test_granular_waste_taxonomy() -> None:
    # 1. Young kids (<10 / toddler nursery rhymes) vs general animation
    assert is_young_kids_text("Cocomelon Nursery Rhymes & Sing-Along") is True
    assert is_young_kids_text("ChuChu TV Toddler Learning Songs") is True
    assert is_young_kids_text("CNN International News Live") is False

    res_toddler = evaluate_heuristics_detailed("Cocomelon Nursery Rhymes", impressions=5000)
    assert res_toddler["category"] == "MADE_FOR_KIDS"
    assert res_toddler["is_young_kids"] is True
    assert res_toddler["granular_sub_category"] == "YOUNG_KIDS_TODDLER"

    res_general = evaluate_heuristics_detailed("Blippi Educational Adventure", impressions=2000)
    assert res_general["category"] == "MADE_FOR_KIDS"
    assert res_general["granular_sub_category"] == "GENERAL_KIDS_CARTOON"

    # 2. Passive music & Underage Gaming granular tags
    res_music = evaluate_heuristics_detailed("Lofi Chill Beats to Sleep/Relax to")
    assert res_music["category"] == "PASSIVE_AUDIO_MUSIC"
    assert res_music["granular_sub_category"] == "PASSIVE_AUDIO_STREAM"

    res_gaming = evaluate_heuristics_detailed("Roblox Brookhaven Roleplay Stream")
    assert res_gaming["category"] == "LOW_AGE_GAMING"
    assert res_gaming["granular_sub_category"] == "LOW_AGE_GAMING_SINK"


def test_impression_weighted_metrics_and_sampling() -> None:
    df = pd.DataFrame(
        [
            {
                "raw_placement": "youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ",
                "channel_id": "UCbCmjCuTUZos6Inko4u57UQ",
                "channel_title": "Cocomelon Nursery Rhymes",
                "placement_type": "YouTube channel",
                "impressions": 8000,
                "views": 2000,
                "clicks": 100,
                "cost": 80.0,
                "conversions": 0.0,
                "currency_code": "EUR",
            },
            {
                "raw_placement": "youtube.com/channel/UCCLEAN11111111111111111",
                "channel_id": "UCCLEAN11111111111111111",
                "channel_title": "Data Engineering Tutorials",
                "placement_type": "YouTube channel",
                "impressions": 2000,
                "views": 800,
                "clicks": 50,
                "cost": 20.0,
                "conversions": 5.0,
                "currency_code": "EUR",
            },
        ]
    )

    # Test sampling by impressions (adapted from an_epro)
    sampled = sample_by_impressions(df, n=1)
    assert len(sampled) == 1

    # Test free audit impression-weighted metrics
    report = run_free_audit(df, print_banner=False)
    assert report.total_impressions_audited == 10000
    assert report.total_wasted_impressions == 8000
    assert report.wasted_impressions_percentage == 80.0
    # Because 80% of impressions are toddler (quality 1.0) and 20% clean (quality 10.0),
    # weighted quality score is approx (1.0*8000 + 10.0*2000) / 10000 = 2.8 / 10
    assert 2.0 <= report.weighted_quality_score <= 3.5

    # Test topic normalization
    assert normalize_topic_category("https://en.wikipedia.org/wiki/Action_game") == "Action game"
    assert normalize_topic_category("https://en.wikipedia.org/wiki/Children%27s_music") == "Children%27s music"


def test_wall_of_shame_html_rendering(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tubesentry_pro = pytest.importorskip("tubesentry_pro")
    # Set fake valid license key for Pro audit
    monkeypatch.setenv("TUBESENTRY_API_KEY", "TS_PRO_VALID_TEST_KEY_24H")

    df = pd.DataFrame(
        [
            {
                "raw_placement": "youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ",
                "channel_id": "UCbCmjCuTUZos6Inko4u57UQ",
                "channel_title": "Cocomelon Nursery Rhymes",
                "placement_type": "YouTube channel",
                "impressions": 15000,
                "views": 3000,
                "clicks": 150,
                "cost": 150.0,
                "conversions": 0.0,
                "currency_code": "EUR",
            }
        ]
    )

    out_html = tmp_path / "deck.html"
    tubesentry_pro.audit_placements_pro(
        df=df,
        api_key="TS_TEST_PRO_LICENSE",
        export_html_deck=str(out_html),
    )

    assert out_html.exists()
    content = out_html.read_text(encoding="utf-8")

    # Assert Wall of Shame spotlight & adapted metrics exist in the HTML output
    assert "Visual Evidence: High-Risk Channel Spotlight" in content
    assert "Placement Quality Score" in content
    assert "Impression Waste Impact" in content
    assert "shame-card" in content
    assert "Toddler" in content
