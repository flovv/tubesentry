from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

import tubesentry
from tubesentry.contracts.exceptions import ProLicenseError
from tubesentry.core.heuristics import evaluate_heuristics
from tubesentry.core.seed_db import lookup_seed_channel
from tubesentry.io.ingestor import extract_youtube_identifiers
from tubesentry.pro.bridge import is_pro_available
from tubesentry.pro.installer import install_pro

mcp = FastMCP("TubeSentry YouTube Placement Auditor")


@mcp.tool()
def audit_placement_report(
    csv_path: str,
    target_languages: list[str] | None = None,
    target_cpa: float | None = None,
    api_key: str | None = None,
    output_dir: str | None = None,
    ad_url: str | None = None,
    ad_text: str | None = None,
    gemini_api_key: str | None = None,
) -> dict[str, Any]:
    """Audits a Google Ads ('Where ads showed') or DV360 YouTube placement CSV report for wasted ad spend
    on Made-for-Kids, Passive Music, Underage Gaming, Foreign Script Leakage, and AI Slop channels.

    If a valid TubeSentry Pro api_key is provided (or installed), automatically writes the 65,000-channel
    Google Ads Editor exclusion CSV and white-label HTML client audit report to output_dir.

    Optionally pass ad_url or ad_text to profile creative targeting intent with Gemini and correlate
    Expectation vs Reality delivery fit.
    """
    if target_languages is None:
        target_languages = ["de", "en"]
    path = Path(csv_path)
    if not path.exists():
        return {"error": f"CSV file not found at: {csv_path}"}

    out_exclusions = None
    out_65k = None
    out_html = None

    effective_key = api_key or os.getenv("TUBESENTRY_API_KEY")
    if output_dir and (is_pro_available() and effective_key):
        out_p = Path(output_dir)
        out_p.mkdir(parents=True, exist_ok=True)
        out_exclusions = str(out_p / "google_ads_reactive_exclusions.csv")
        out_65k = str(out_p / "google_ads_65k_full_shield.csv")
        out_html = str(out_p / "youtube_waste_audit.html")

    try:
        report = tubesentry.audit_placements(
            report=csv_path,
            target_languages=target_languages,
            target_cpa=target_cpa,
            api_key=api_key,
            export_exclusions_csv=out_exclusions,
            export_65k_shield_csv=out_65k,
            export_html_deck=out_html,
            print_banner=False,
            ad_url=ad_url,
            ad_text=ad_text,
            gemini_api_key=gemini_api_key,
        )
        return report.model_dump()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def profile_creative_intent(
    ad_url: str | None = None,
    ad_text: str | None = None,
    gemini_api_key: str | None = None,
) -> dict[str, Any]:
    """Analyzes a YouTube video ad URL or creative brief with Gemini to determine the Ideal Customer Profile (ICP),
    recommended YouTube contextual topic entities, and negative anti-persona exclusions.
    """
    try:
        from tubesentry_pro.creative_profiler import profile_ad_creative  # type: ignore[import-not-found,import-untyped]

        profile = profile_ad_creative(
            ad_url=ad_url,
            ad_text=ad_text,
            gemini_api_key=gemini_api_key,
        )
        return profile.model_dump()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def inspect_youtube_channels(
    channel_ids_or_urls: list[str],
    target_languages: list[str] | None = None,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """Looks up specific YouTube Channel IDs or URLs in the TubeSentry Intelligence Database
    to check madeForKids status, audio language, topic categories, and waste risk score.
    """
    if target_languages is None:
        target_languages = ["de", "en"]
    results: list[dict[str, Any]] = []

    # Check if Pro classifier is available
    pro_classifier = None
    if is_pro_available():
        try:
            import tubesentry_pro.classifier as pro_classifier  # type: ignore[no-redef]
        except Exception:
            pass

    for item in channel_ids_or_urls:
        ch_id, _handle = extract_youtube_identifiers(item)
        lookup_id = ch_id or item

        # Check Seed DB
        seed = lookup_seed_channel(lookup_id) if ch_id else None
        if seed:
            results.append({
                "input": item,
                "channel_id": seed["channel_id"],
                "channel_title": seed["title"],
                "waste_category": seed["category"],
                "waste_confidence": seed["confidence"],
                "reason_summary": seed["reason"],
                "database_source": "seed_db",
            })
            continue

        # Check Pro registry if available
        if pro_classifier and hasattr(pro_classifier, "lookup_registry"):
            reg_entry = pro_classifier.lookup_registry(lookup_id)
            if reg_entry:
                results.append({
                    "input": item,
                    "channel_id": reg_entry.get("channel_id", lookup_id),
                    "channel_title": reg_entry.get("title", item),
                    "waste_category": reg_entry.get("category", "CLEAN"),
                    "waste_confidence": reg_entry.get("confidence", 0.95),
                    "reason_summary": "Matched in TubeSentry Pro 250k Registry",
                    "database_source": "pro_250k_registry",
                })
                continue

        # Heuristic fallback
        cat, conf, reason = evaluate_heuristics(
            channel_title=item,
            raw_placement=item,
            target_languages=target_languages,
        )
        results.append({
            "input": item,
            "channel_id": ch_id or lookup_id,
            "channel_title": item,
            "waste_category": cat,
            "waste_confidence": conf,
            "reason_summary": reason,
            "database_source": "heuristics",
        })

    return results


@mcp.tool()
def activate_tubesentry_pro(api_key: str) -> dict[str, Any]:
    """Validates a Polar.sh TubeSentry Pro license key (TS_PRO_...) and installs the compiled
    tubesentry_pro binary wheel and 250k channel database.
    """
    try:
        success = install_pro(api_key)
        if success:
            return {
                "status": "success",
                "message": "TubeSentry Pro successfully activated and installed.",
                "pro_available": is_pro_available(),
            }
        return {
            "status": "failed",
            "message": "Installation failed without error details.",
            "pro_available": is_pro_available(),
        }
    except ProLicenseError as e:
        return {"status": "license_error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main() -> None:
    """CLI entrypoint for running the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
