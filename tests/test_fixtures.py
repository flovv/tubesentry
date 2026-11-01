from __future__ import annotations

from pathlib import Path

from tubesentry.io.fixtures import generate_synthetic_placement_csv
from tubesentry.io.ingestor import load_placement_report


def test_generate_synthetic_placement_csv(tmp_path: Path) -> None:
    csv_file = tmp_path / "synthetic_test.csv"
    res_path = generate_synthetic_placement_csv(
        output_path=csv_file,
        num_rows=200,
        seed=123,
        language="de",
    )
    assert res_path.exists()

    df = load_placement_report(res_path)
    assert len(df) == 200
    assert df["cost"].sum() > 0
    assert df["impressions"].sum() > 0
    assert "channel_id" in df.columns
