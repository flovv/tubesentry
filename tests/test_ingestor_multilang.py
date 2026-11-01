from __future__ import annotations

from pathlib import Path

import pytest

from tubesentry.contracts.exceptions import MalformedPlacementCSVError
from tubesentry.io.ingestor import load_placement_report, parse_localized_numeric


def test_parse_localized_numeric_variants() -> None:
    # European currency & separators
    assert parse_localized_numeric("1.234,56 €") == 1234.56
    assert parse_localized_numeric("1450,20 €") == 1450.20
    assert parse_localized_numeric("45,00") == 45.0
    # Anglo currency & separators
    assert parse_localized_numeric("$1,234.56") == 1234.56
    assert parse_localized_numeric("1450.20") == 1450.20
    # Integer values
    assert parse_localized_numeric("5000") == 5000.0
    assert parse_localized_numeric(42) == 42.0
    # Empty and dashes
    assert parse_localized_numeric("--") == 0.0
    assert parse_localized_numeric("< 10%") == 0.0
    assert parse_localized_numeric(None) == 0.0


def test_english_google_ads_export_with_headers_and_footer(tmp_path: Path) -> None:
    csv_content = """Where ads showed report
Date range: Last 30 days
Account ID: 123-456-7890

Where ads showed,Placement name,Cost,Impr.,Views,Clicks,Conversions
youtube.com/channel/UCbCmjCuTUZos6Inko4u57UQ,Cocomelon,$450.25,12000,3400,120,0.0
youtube.com/channel/UCSJ4gkVC6NrvII8umztf0Ow,Lofi Girl,$230.10,8500,2100,45,0.0
Total: Account,--,$680.35,20500,5500,165,0.0
"""
    file_path = tmp_path / "google_ads_en.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    df = load_placement_report(file_path)

    assert len(df) == 2
    assert "UCbCmjCuTUZos6Inko4u57UQ" in df["channel_id"].values
    assert "UCSJ4gkVC6NrvII8umztf0Ow" in df["channel_id"].values
    assert round(df["cost"].sum(), 2) == 680.35
    assert df["impressions"].sum() == 20500
    assert not any("Total" in str(x) for x in df["raw_placement"])


def test_german_google_ads_export_with_commas_and_gesamt(tmp_path: Path) -> None:
    csv_content = """Bericht: Wo Anzeigen geschaltet wurden
Zeitraum: Letzte 30 Tage
Währung: EUR

Placement,Name des Placements,Kosten,Impressionen,Aufrufe,Klicks,Konversionen
youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA,Baby Shark,"1.234,56 €","25.000",6200,350,"1,0"
youtube.com/channel/UCvlE5gTbOvjiolFlEm-c_Ow,Vlad and Niki,"765,44 €",15000,4100,190,"0,0"
Gesamt: Konto,--,"2.000,00 €","40.000",10300,540,"1,0"
"""
    file_path = tmp_path / "google_ads_de.csv"
    file_path.write_text(csv_content, encoding="utf-8-sig")

    df = load_placement_report(file_path)

    assert len(df) == 2
    assert "UCX6OQ3DkcsbYNE6H8uQQuVA" in df["channel_id"].values
    assert "UCvlE5gTbOvjiolFlEm-c_Ow" in df["channel_id"].values
    assert round(df["cost"].sum(), 2) == 2000.00
    assert df.loc[df["channel_id"] == "UCX6OQ3DkcsbYNE6H8uQQuVA", "cost"].iloc[0] == 1234.56
    assert df.loc[df["channel_id"] == "UCvlE5gTbOvjiolFlEm-c_Ow", "cost"].iloc[0] == 765.44


def test_spanish_placement_export(tmp_path: Path) -> None:
    csv_content = """Informe de emplazamientos
Rango: Todo el periodo

Emplazamiento,Nombre del emplazamiento,Coste,Impresiones,Visualizaciones,Clics,Conversiones
youtube.com/channel/UCbmT_5p1XmZ3Nl9wXhB9xQw,El Reino Infantil,340.50,9200,1800,95,0.0
youtube.com/channel/UCq-GFYZe9K9_mQG9F_1QZow,T-Series,150.20,4500,900,40,0.0
Resumen: Total,--,490.70,13700,2700,135,0.0
"""
    file_path = tmp_path / "google_ads_es.csv"
    file_path.write_text(csv_content, encoding="utf-8")

    df = load_placement_report(file_path)

    assert len(df) == 2
    assert "UCbmT_5p1XmZ3Nl9wXhB9xQw" in df["channel_id"].values
    assert round(df["cost"].sum(), 2) == 490.70


def test_malformed_csv_raises_error(tmp_path: Path) -> None:
    bad_csv = """Random file without headers
Line 1
Line 2
Line 3
"""
    file_path = tmp_path / "bad.csv"
    file_path.write_text(bad_csv, encoding="utf-8")

    with pytest.raises(MalformedPlacementCSVError):
        load_placement_report(file_path)
