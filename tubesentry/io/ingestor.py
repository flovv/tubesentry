from __future__ import annotations

import io
import re
from pathlib import Path
from typing import BinaryIO, TextIO

import pandas as pd

from tubesentry.contracts.exceptions import MalformedPlacementCSVError

# Regex patterns for Channel and Video IDs
CHANNEL_ID_REGEX = re.compile(r"UC[a-zA-Z0-9_-]{22}")
DIRECT_CHANNEL_ID_REGEX = re.compile(r"^UC[a-zA-Z0-9_-]{22}$")
URL_CHANNEL_ID_REGEX = re.compile(r"youtube\.com/channel/(UC[a-zA-Z0-9_-]{22})")
URL_HANDLE_REGEX = re.compile(r"(?:youtube\.com/)?@([a-zA-Z0-9_.-]+)")
URL_VIDEO_REGEX = re.compile(
    r"(?:youtube\.com/(?:watch\?v=|video/|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})"
)

# Canonical Column Alias Dictionary (lowercase stripped for robust matching)
COLUMN_ALIASES: dict[str, list[str]] = {
    "raw_placement": [
        "placement",
        "placement url",
        "where ads showed",
        "emplazamiento",
        "emplacement",
        "posizionamento",
        "plaatsing",
        "youtube channel",
        "app/url",
        "wo anzeigen geschaltet wurden",
    ],
    "channel_title": [
        "placement name",
        "name des placements",
        "nombre del emplazamiento",
        "channel name",
        "nom de l'emplacement",
        "nome del posizionamento",
        "plaatsingsnaam",
        "channel",
        "kanalname",
    ],
    "cost": [
        "cost",
        "kosten",
        "coste",
        "coût",
        "cout",
        "costo",
        "media cost",
        "spend",
        "revenue (adv currency)",
        "ausgaben",
    ],
    "impressions": [
        "impr.",
        "impressions",
        "impressionen",
        "impresiones",
        "impressies",
        "impressioni",
    ],
    "views": [
        "views",
        "aufrufe",
        "visualizaciones",
        "vues",
        "trueview views",
        "visualizzazioni",
        "weergaven",
    ],
    "clicks": [
        "clicks",
        "klicks",
        "clics",
        "clic",
        "klikken",
    ],
    "conversions": [
        "conversions",
        "conv.",
        "konversionen",
        "conversiones",
        "conversies",
    ],
}


def extract_youtube_identifiers(
    placement: str,
) -> tuple[str | None, str | None]:
    """Extracts canonical 24-character YouTube Channel ID or handle/video ID.

    Returns:
        tuple[channel_id, handle_or_video_id]
    """
    if not placement or not isinstance(placement, str):
        return None, None

    cleaned = placement.strip()

    # 1. Direct 24-char UC channel ID
    if DIRECT_CHANNEL_ID_REGEX.match(cleaned):
        return cleaned, None

    # 2. URL containing /channel/UC...
    match_url_ch = URL_CHANNEL_ID_REGEX.search(cleaned)
    if match_url_ch:
        return match_url_ch.group(1), None

    # 3. Embedded UC regex search anywhere in placement
    match_ch = CHANNEL_ID_REGEX.search(cleaned)
    if match_ch:
        return match_ch.group(0), None

    # 4. Handle fallback (@name)
    match_handle = URL_HANDLE_REGEX.search(cleaned)
    if match_handle:
        return None, f"@{match_handle.group(1)}"

    # 5. Video ID fallback
    match_vid = URL_VIDEO_REGEX.search(cleaned)
    if match_vid:
        return None, match_vid.group(1)

    return None, None


def parse_localized_numeric(val: object) -> float:
    """Parses numeric values supporting European ('1.450,20') and Anglo ('1,450.20') formats."""
    if val is None or pd.isna(val):
        return 0.0

    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip()
    if not s or s in ("--", "-", "null", "None", "< 10%", "auto"):
        return 0.0

    # Strip currency signs, quotes and whitespace
    s = re.sub(r"[€$£CHF¥\s%\"']", "", s)

    # Detect delimiter structure
    # e.g., 1.450,20 (European: dot thousand, comma decimal)
    # vs 1,450.20 (Anglo: comma thousand, dot decimal)
    if "," in s and "." in s:
        last_comma = s.rfind(",")
        last_dot = s.rfind(".")
        if last_comma > last_dot:
            # European: remove dots, change comma to dot
            s = s.replace(".", "").replace(",", ".")
        else:
            # Anglo: remove commas
            s = s.replace(",", "")
    elif "," in s:
        # Could be decimal comma '1450,20' or thousands '1,450'
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) in (1, 2, 4):  # e.g. currency cents
            s = s.replace(",", ".")
        elif len(parts) == 2 and len(parts[1]) == 3:  # thousands like 1,000
            s = s.replace(",", "")
        else:
            s = s.replace(",", "")

    try:
        return float(s)
    except ValueError:
        return 0.0


def _detect_encoding_and_content(source: str | Path | BinaryIO | TextIO) -> tuple[str, str]:
    """Reads source text detecting UTF-8, UTF-8-SIG, UTF-16LE, or Latin-1 encodings."""
    raw_bytes: bytes

    if isinstance(source, (str, Path)):
        p = Path(source)
        if not p.exists():
            raise FileNotFoundError(f"Placement report file not found: {source}")
        raw_bytes = p.read_bytes()
    elif hasattr(source, "read"):
        content = source.read()
        if isinstance(content, str):
            return "utf-8", content
        raw_bytes = content
    else:
        raise MalformedPlacementCSVError(f"Unsupported source type: {type(source)}")

    # Try encodings in order
    for enc in ["utf-8-sig", "utf-8", "utf-16le", "utf-16", "latin-1"]:
        try:
            decoded = raw_bytes.decode(enc)
            return enc, decoded
        except (UnicodeDecodeError, LookupError):
            continue

    return "latin-1", raw_bytes.decode("latin-1", errors="replace")


def _find_header_row_offset(lines: list[str]) -> tuple[int, str]:
    """Scans the first 15 lines of CSV/TSV to discover header offset and delimiter."""
    for idx, line in enumerate(lines[:15]):
        line_clean = line.strip().lower()
        if not line_clean:
            continue

        # Check potential delimiters
        for delim in [",", "\t", ";"]:
            tokens = [t.strip().strip('"').strip("'") for t in line_clean.split(delim)]

            has_placement = any(
                any(alias == t or alias in t for alias in COLUMN_ALIASES["raw_placement"])
                for t in tokens
            )
            has_metric = any(
                any(
                    alias == t or alias in t
                    for alias in (COLUMN_ALIASES["cost"] + COLUMN_ALIASES["impressions"])
                )
                for t in tokens
            )

            if has_placement and has_metric:
                return idx, delim

    raise MalformedPlacementCSVError(
        "Could not detect valid Google Ads or DV360 placement tabular header row within first 15 lines. "
        "Ensure the file includes placement and cost/impression columns."
    )


def load_placement_report(
    path_or_df: str | Path | pd.DataFrame | TextIO | BinaryIO,
) -> pd.DataFrame:
    """Auto-detects Google Ads or DV360 CSV header offsets across EN/DE/ES/FR/IT/NL,
    extracts canonical 24-char YouTube Channel IDs, and normalizes spend and metrics.

    Returns:
        pd.DataFrame with columns:
        - raw_placement: str
        - channel_id: Optional[str] (24-char UC...)
        - handle_or_video_id: Optional[str]
        - channel_title: str
        - placement_type: str
        - impressions: int
        - views: int
        - clicks: int
        - cost: float
        - conversions: float
        - currency_code: str
    """
    if isinstance(path_or_df, pd.DataFrame):
        df_raw = path_or_df.copy()
    else:
        _encoding, text = _detect_encoding_and_content(path_or_df)
        lines = [line for line in text.splitlines() if line.strip()]
        if not lines:
            raise MalformedPlacementCSVError("Placement report is empty.")

        offset, delim = _find_header_row_offset(lines)
        csv_buffer = io.StringIO("\n".join(lines[offset:]))
        try:
            df_raw = pd.read_csv(csv_buffer, sep=delim, dtype=str, on_bad_lines="skip")
        except Exception as e:
            raise MalformedPlacementCSVError(f"Failed to parse placement CSV: {e}") from e

    # Map column headers to canonical names (exact match first, then substring fallback)
    matched_cols: dict[str, str] = {}
    normalized_col_map = {str(c).strip().lower(): c for c in df_raw.columns}

    # Pass 1: Exact matches
    for canonical_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            for norm_c, orig_c in normalized_col_map.items():
                if norm_c == alias and orig_c not in matched_cols.values():
                    matched_cols[canonical_name] = orig_c
                    break
            if canonical_name in matched_cols:
                break

    # Pass 2: Substring matches for unmapped columns
    for canonical_name, aliases in COLUMN_ALIASES.items():
        if canonical_name in matched_cols:
            continue
        for alias in aliases:
            for norm_c, orig_c in normalized_col_map.items():
                if alias in norm_c and orig_c not in matched_cols.values() and len(norm_c) < len(alias) + 12:
                    matched_cols[canonical_name] = orig_c
                    break
            if canonical_name in matched_cols:
                break

    if "raw_placement" not in matched_cols:
        raise MalformedPlacementCSVError(
            f"Missing required placement column. Detected columns: {list(df_raw.columns)}"
        )

    # Filter out footer rows (e.g. Total, Gesamt, Summe)
    raw_col = matched_cols["raw_placement"]
    df_filtered = df_raw[df_raw[raw_col].notna()].copy()
    df_filtered[raw_col] = df_filtered[raw_col].astype(str).str.strip()

    footer_pattern = re.compile(
        r"^(?:total|gesamt|summe|resumen|subtotal|all|account total|campaign total|group total)",
        re.IGNORECASE,
    )
    df_filtered = df_filtered[~df_filtered[raw_col].str.contains(footer_pattern)]
    df_filtered = df_filtered[df_filtered[raw_col] != ""]

    if df_filtered.empty:
        raise MalformedPlacementCSVError("Report contains no valid placement rows after removing footers.")

    # Build standardized dataframe
    rows: list[dict] = []
    title_col = matched_cols.get("channel_title")
    cost_col = matched_cols.get("cost")
    impr_col = matched_cols.get("impressions")
    views_col = matched_cols.get("views")
    clicks_col = matched_cols.get("clicks")
    conv_col = matched_cols.get("conversions")

    for _, row in df_filtered.iterrows():
        raw_val = str(row[raw_col]).strip()
        ch_id, handle_or_vid = extract_youtube_identifiers(raw_val)

        title_val = ""
        if title_col and pd.notna(row.get(title_col)):
            title_val = str(row[title_col]).strip()
        if not title_val:
            title_val = raw_val

        cost_val = parse_localized_numeric(row.get(cost_col)) if cost_col else 0.0
        impr_val = round(parse_localized_numeric(row.get(impr_col))) if impr_col else 0
        views_val = round(parse_localized_numeric(row.get(views_col))) if views_col else 0
        clicks_val = round(parse_localized_numeric(row.get(clicks_col))) if clicks_col else 0
        conv_val = parse_localized_numeric(row.get(conv_col)) if conv_col else 0.0

        rows.append(
            {
                "raw_placement": raw_val,
                "channel_id": ch_id,
                "handle_or_video_id": handle_or_vid,
                "channel_title": title_val,
                "placement_type": "YouTube channel" if (ch_id or "youtube.com" in raw_val) else "Website/App",
                "impressions": impr_val,
                "views": views_val,
                "clicks": clicks_val,
                "cost": round(cost_val, 2),
                "conversions": round(conv_val, 2),
                "currency_code": "EUR",
            }
        )

    return pd.DataFrame(rows)


def sample_by_impressions(
    df: pd.DataFrame,
    n: int = 100,
    random_state: int | None = 42,
) -> pd.DataFrame:
    """Samples n rows proportional to impression volume (prob = impressions / sum(impressions)).

    Adapted from agency audit methodologies to prioritize high-spend waste channels
    statistically when audit API quotas or processing limits apply.
    """
    if df.empty or len(df) <= n:
        return df.copy()

    impr_series = df["impressions"].fillna(0).clip(lower=0)
    total_impr = impr_series.sum()
    if total_impr <= 0:
        return df.sample(n=min(n, len(df)), random_state=random_state)

    weights = impr_series / total_impr
    return df.sample(n=min(n, len(df)), weights=weights, random_state=random_state)
