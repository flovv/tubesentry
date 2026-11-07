from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from tubesentry.cli import app
from tubesentry.pro import bridge

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "TubeSentry" in result.output
    assert "audit" in result.output
    assert "demo" in result.output
    assert "auth" in result.output
    assert "skill" in result.output
    assert "export" in result.output


def test_cli_demo(tmp_path: Path) -> None:
    demo_dir = tmp_path / "demo_test"
    result = runner.invoke(app, ["demo", "--out-dir", str(demo_dir), "--rows", "100"])
    assert result.exit_code == 0
    csv_file = demo_dir / "google_ads_where_ads_showed_sample.csv"
    assert csv_file.exists()
    assert "TUBESENTRY OPEN-CORE" in result.output or "WASTED BUDGET BY CATEGORY" in result.output


def test_cli_audit(tmp_path: Path) -> None:
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        """Placement,Placement name,Cost,Impr.,Views,Clicks,Conversions
youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ,Cocomelon,100.00,5000,1000,20,0.0
""",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["audit", str(csv_file)])
    assert result.exit_code == 0
    assert "Audited Placements" in result.output


def test_cli_auth_test_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bridge, "HAS_PRO", bridge.HAS_PRO)
    monkeypatch.delenv("TUBESENTRY_API_KEY", raising=False)
    result = runner.invoke(app, ["auth", "--key", "TS_TEST_DEV_KEY"])
    assert result.exit_code == 0
    assert "License validated successfully" in result.output
