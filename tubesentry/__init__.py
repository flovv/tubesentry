from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

from tubesentry.contracts.schemas import AuditSummaryReport
from tubesentry.core.auditor import run_free_audit
from tubesentry.io.ingestor import load_placement_report
from tubesentry.pro.bridge import dispatch_pro_audit, is_pro_available
from tubesentry.pro.installer import install_pro

__version__ = "0.1.0"


def audit_placements(
    report: str | Path | pd.DataFrame,
    target_languages: list[str] | None = None,
    target_cpa: float | None = None,
    api_key: str | None = None,
    youtube_api_key: str | None = None,
    export_exclusions_csv: str | None = None,
    export_65k_shield_csv: str | None = None,
    export_html_deck: str | None = None,
    white_label_config: dict[str, Any] | None = None,
    print_banner: bool = True,
    ad_url: str | None = None,
    ad_text: str | None = None,
    gemini_api_key: str | None = None,
) -> AuditSummaryReport:
    """Audits Google Ads ('Where ads showed') or DV360 YouTube placement reports for ad waste.

    - Free Mode (default): Computes exact waste totals across all 6 categories,
      unmasks the Top 25 worst offending channels, and prints the diagnostic banner.
    - Pro Mode (with valid `api_key` and `tubesentry_pro` installed): Uses the 250k
      channel intelligence registry, 50-ID batch API enrichment, unmasks all channels,
      evaluates Gemini creative targeting fit, and exports Google Ads Editor exclusion files & white-label HTML deck.
    """
    langs = target_languages or ["de", "en"]
    df = load_placement_report(report) if not isinstance(report, pd.DataFrame) else report

    effective_key = api_key or os.getenv("TUBESENTRY_API_KEY")

    # If Pro is available and a license key is provided (or Pro exports requested)
    if is_pro_available() and effective_key:
        return dispatch_pro_audit(
            df=df,
            target_languages=langs,
            target_cpa=target_cpa,
            api_key=effective_key,
            youtube_api_key=youtube_api_key,
            export_exclusions_csv=export_exclusions_csv,
            export_65k_shield_csv=export_65k_shield_csv,
            export_html_deck=export_html_deck,
            white_label_config=white_label_config,
            ad_url=ad_url,
            ad_text=ad_text,
            gemini_api_key=gemini_api_key,
        )

    # If caller specifically requested Pro exports without Pro/license, route through dispatcher to surface upgrade error
    if export_exclusions_csv or export_65k_shield_csv or export_html_deck or ad_url or ad_text:
        return dispatch_pro_audit(
            df=df,
            target_languages=langs,
            target_cpa=target_cpa,
            api_key=effective_key,
            youtube_api_key=youtube_api_key,
            export_exclusions_csv=export_exclusions_csv,
            export_65k_shield_csv=export_65k_shield_csv,
            export_html_deck=export_html_deck,
            white_label_config=white_label_config,
            ad_url=ad_url,
            ad_text=ad_text,
            gemini_api_key=gemini_api_key,
        )

    return run_free_audit(
        df=df,
        target_languages=langs,
        target_cpa=target_cpa,
        print_banner=print_banner,
    )


__all__ = [
    "AuditSummaryReport",
    "__version__",
    "audit_placements",
    "install_pro",
    "is_pro_available",
    "load_placement_report",
]
