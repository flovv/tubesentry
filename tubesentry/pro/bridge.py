from __future__ import annotations

import os
from typing import Any

import pandas as pd

from tubesentry.contracts.exceptions import ProFeatureNotInstalledError, ProLicenseError
from tubesentry.contracts.schemas import AuditSummaryReport

# Attempt dynamic import of compiled tubesentry_pro package
try:
    import tubesentry_pro
    HAS_PRO = True
except ImportError:
    tubesentry_pro = None  # type: ignore[assignment]
    HAS_PRO = False


def is_pro_available() -> bool:
    """Returns True if the tubesentry_pro proprietary binary package is installed."""
    return HAS_PRO


def dispatch_pro_audit(
    df: pd.DataFrame,
    target_languages: list[str] | None = None,
    target_cpa: float | None = None,
    api_key: str | None = None,
    youtube_api_key: str | None = None,
    export_exclusions_csv: str | None = None,
    export_65k_shield_csv: str | None = None,
    export_html_deck: str | None = None,
    white_label_config: dict[str, Any] | None = None,
    ad_url: str | None = None,
    ad_text: str | None = None,
    gemini_api_key: str | None = None,
) -> AuditSummaryReport:
    """Safely dispatches placement audit to compiled `tubesentry_pro` binary.

    Raises:
        ProFeatureNotInstalledError: If tubesentry_pro is not installed.
        ProLicenseError: If license validation fails or key is missing.
    """
    if not HAS_PRO or tubesentry_pro is None:
        raise ProFeatureNotInstalledError(
            "🔒 TubeSentry Pro is required to unlock all flagged channels, generate the 65,000-channel "
            "Google Ads Editor exclusion file, batch-enrich unknown channels, and compile the HTML deck.\n"
            "To install the Pro binary:\n"
            "    >>> import tubesentry as ts\n"
            "    >>> ts.install_pro(api_key='TS_PRO_...')\n"
            "Or run CLI:\n"
            "    $ tubesentry auth --key TS_PRO_...\n"
            "Obtain a key at https://tubesentry.dev"
        )

    effective_key = api_key or os.getenv("TUBESENTRY_API_KEY", "")
    if not effective_key:
        raise ProLicenseError(
            "🔒 TubeSentry Pro license key required. Pass `api_key='TS_PRO_...'` or set TUBESENTRY_API_KEY.\n"
            "Obtain a key at https://tubesentry.dev"
        )

    return tubesentry_pro.audit_placements_pro(
        df=df,
        target_languages=target_languages,
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
