from __future__ import annotations

from pathlib import Path

from tubesentry.mcp_server import (
    activate_tubesentry_pro,
    audit_placement_report,
    inspect_youtube_channels,
)


def test_inspect_youtube_channels() -> None:
    inputs = [
        "UCbCmjCuTUZos6Inko4u57UQ",  # Cocomelon
        "https://www.youtube.com/channel/UCSJ4gkVC6NrvII8umztf0Ow",  # Lofi Girl
        "https://www.youtube.com/channel/UCq-GFYZe9K9_mQG9F_1QZow",  # T-Series Hindi
        "https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ",  # MKBHD (Clean)
    ]
    results = inspect_youtube_channels(inputs)

    assert len(results) == 4
    categories = [r["waste_category"] for r in results]
    assert "MADE_FOR_KIDS" in categories
    assert "PASSIVE_AUDIO_MUSIC" in categories


def test_audit_placement_report_tool(tmp_path: Path) -> None:
    csv_file = tmp_path / "report.csv"
    csv_file.write_text(
        """Placement,Placement name,Cost,Impr.,Views,Clicks,Conversions
youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ,Cocomelon,500.00,10000,2000,50,0.0
youtube.com/channel/UCSJ4gkVC6NrvII8umztf0Ow,Lofi Girl,200.00,8000,1500,30,0.0
""",
        encoding="utf-8",
    )

    out_dir = tmp_path / "audit_output"
    result = audit_placement_report(
        csv_path=str(csv_file),
        target_languages=["de", "en"],
        output_dir=str(out_dir),
    )

    assert "total_spend" in result
    assert result["total_spend"] == 700.00
    assert result["total_wasted_spend"] == 700.00
    assert len(result["top_offenders"]) == 2


def test_activate_tubesentry_pro_mock() -> None:
    # Use dev/test key pattern
    res = activate_tubesentry_pro(api_key="TS_TEST_AGENCY_SECRET_KEY")
    assert res["status"] == "success"
    assert res["pro_available"] is True
