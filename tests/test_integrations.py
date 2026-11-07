from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from tubesentry import audit_placements, generate_bigquery_dts_sql, generate_google_ads_script
from tubesentry.cli import app
from tubesentry.mcp_server import export_bigquery_dts_sql, export_google_ads_script

runner = CliRunner()


def test_generate_google_ads_script() -> None:
    channels = ["UCbCmjCuTUZos6Inko4u57UQ", "UCSJ4gkVC6NrvII8umztf0Ow"]
    js_code = generate_google_ads_script(
        channel_ids_or_urls=channels,
        dry_run=True,
        mode="SHARED_LIST",
        shared_list_name="PPC Waste Shield",
    )

    assert "TubeSentry Automated Placement Exclusion Script" in js_code
    assert "DRY_RUN: true" in js_code
    assert "SHARED_LIST_NAME: 'PPC Waste Shield'" in js_code
    assert "UCbCmjCuTUZos6Inko4u57UQ" in js_code
    assert "applyToSharedList" in js_code
    assert "AdsApp.excludedPlacementLists()" in js_code


def test_generate_google_ads_script_campaign_mode() -> None:
    channels = ["UC1234567890123456789012"]
    js_code = generate_google_ads_script(
        channel_ids_or_urls=channels,
        dry_run=False,
        mode="CAMPAIGNS",
        campaign_name_contains="YouTube - Core",
    )

    assert "DRY_RUN: false" in js_code
    assert "EXCLUSION_MODE: 'CAMPAIGNS'" in js_code
    assert "CAMPAIGN_NAME_CONTAINS: 'YouTube - Core'" in js_code
    assert "applyToCampaigns" in js_code
    assert "AdsApp.videoCampaigns()" in js_code


def test_generate_bigquery_dts_sql() -> None:
    sql = generate_bigquery_dts_sql(
        dataset="my_google_ads_dataset",
        customer_id="9876543210",
        lookback_days=45,
        target_cpa=35.0,
        as_dbt=False,
    )

    assert "WITH raw_placements AS" in sql
    assert "`my_google_ads_dataset.p_Placement_9876543210`" in sql
    assert "INTERVAL 45 DAY" in sql
    assert "is_made_for_kids" in sql
    assert "is_passive_music" in sql
    assert "is_underage_gaming" in sql
    assert "is_foreign_script" in sql
    assert "is_performance_sinkhole" in sql
    assert "quality_score" in sql
    assert "formatted_exclusion_url" in sql


def test_generate_bigquery_dts_sql_dbt_mode() -> None:
    sql = generate_bigquery_dts_sql(as_dbt=True)
    assert "{{ config(" in sql
    assert "materialized = 'table'" in sql
    assert "cluster_by = ['waste_category', 'channel_id']" in sql


def test_audit_placements_export_script(tmp_path: Path) -> None:
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        """Placement,Placement name,Cost,Impr.,Views,Clicks,Conversions
youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ,Cocomelon,100.00,5000,1000,20,0.0
""",
        encoding="utf-8",
    )

    out_script = tmp_path / "cleanup.js"
    audit_placements(
        report=csv_file,
        export_google_ads_script=str(out_script),
        print_banner=False,
    )

    assert out_script.exists()
    content = out_script.read_text(encoding="utf-8")
    assert "UCbCmjCuTUZos6Inko4u57UQ" in content
    assert "AdsApp" in content


def test_cli_audit_with_export_script(tmp_path: Path) -> None:
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        """Placement,Placement name,Cost,Impr.,Views,Clicks,Conversions
youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ,Cocomelon,50.00,2000,500,10,0.0
""",
        encoding="utf-8",
    )
    out_script = tmp_path / "cli_cleanup.js"
    res = runner.invoke(app, ["audit", str(csv_file), "--export-script", str(out_script)])
    assert res.exit_code == 0
    assert out_script.exists()
    assert "Exported Google Ads JavaScript automation" in res.output


def test_cli_export_commands(tmp_path: Path) -> None:
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        """Placement,Placement name,Cost,Impr.,Views,Clicks,Conversions
youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ,Cocomelon,50.00,2000,500,10,0.0
""",
        encoding="utf-8",
    )

    # 1. export script
    out_js = tmp_path / "out.js"
    res_js = runner.invoke(
        app,
        [
            "export",
            "script",
            "--report",
            str(csv_file),
            "--out",
            str(out_js),
            "--list-name",
            "Test Shield",
        ],
    )
    assert res_js.exit_code == 0
    assert out_js.exists()
    assert "Test Shield" in out_js.read_text(encoding="utf-8")

    # 2. export bigquery
    out_sql = tmp_path / "query.sql"
    res_sql = runner.invoke(
        app,
        [
            "export",
            "bigquery",
            "--out",
            str(out_sql),
            "--dataset",
            "analytics_ads",
            "--customer-id",
            "123",
            "--dbt",
        ],
    )
    assert res_sql.exit_code == 0
    assert out_sql.exists()
    sql_text = out_sql.read_text(encoding="utf-8")
    assert "analytics_ads.p_Placement_123" in sql_text
    assert "{{ config(" in sql_text


def test_mcp_export_tools() -> None:
    # 1. Google Ads Script tool
    res_tool = export_google_ads_script(
        channel_ids=["UCbCmjCuTUZos6Inko4u57UQ"],
        dry_run=True,
    )
    assert res_tool["status"] == "success"
    assert "UCbCmjCuTUZos6Inko4u57UQ" in res_tool["javascript_code"]

    # 2. BigQuery DTS tool
    sql = export_bigquery_dts_sql(dataset="dts_dataset", customer_id="555")
    assert "dts_dataset.p_Placement_555" in sql
