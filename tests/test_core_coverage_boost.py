from __future__ import annotations

import io

import pandas as pd
import pytest

from tubesentry import install_pro
from tubesentry.contracts.exceptions import ProFeatureNotInstalledError, ProLicenseError
from tubesentry.io.ingestor import load_placement_report
from tubesentry.mcp_server import audit_placement_report
from tubesentry.pro import bridge


def test_load_placement_report_from_dataframe() -> None:
    df_in = pd.DataFrame(
        [
            {
                "Placement": "youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ",
                "Placement name": "Cocomelon",
                "Cost": "50.00",
                "Impr.": "1000",
            }
        ]
    )
    df_out = load_placement_report(df_in)
    assert len(df_out) == 1
    assert df_out["channel_id"].iloc[0] == "UCbCmjCuTUZos6Inko4u57UQ"


def test_load_placement_report_from_textio() -> None:
    csv_str = """Placement,Placement name,Cost,Impr.
youtube.com/channel/UCSJ4gkVC6NrvII8umztf0Ow,Lofi Girl,30.00,500
"""
    stream = io.StringIO(csv_str)
    df = load_placement_report(stream)
    assert len(df) == 1
    assert df["channel_id"].iloc[0] == "UCSJ4gkVC6NrvII8umztf0Ow"


def test_installer_empty_key_error() -> None:
    with pytest.raises(ProLicenseError, match="must not be empty"):
        install_pro("")


def test_bridge_pro_not_installed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bridge, "HAS_PRO", False)
    monkeypatch.setattr(bridge, "tubesentry_pro", None)

    df = pd.DataFrame([{"cost": 10.0, "impressions": 100, "raw_placement": "test"}])
    with pytest.raises(ProFeatureNotInstalledError, match="TubeSentry Pro is required"):
        bridge.dispatch_pro_audit(df, api_key="KEY")


def test_bridge_pro_missing_key_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bridge, "HAS_PRO", True)
    monkeypatch.setattr(bridge, "tubesentry_pro", object())
    monkeypatch.delenv("TUBESENTRY_API_KEY", raising=False)

    df = pd.DataFrame([{"cost": 10.0, "impressions": 100, "raw_placement": "test"}])
    with pytest.raises(ProLicenseError, match="license key required"):
        bridge.dispatch_pro_audit(df, api_key="")


def test_mcp_missing_file_error() -> None:
    res = audit_placement_report("/non/existent/path/file.csv")
    assert "error" in res
