from __future__ import annotations

from collections import defaultdict
from typing import Any

import pandas as pd
from rich.console import Console

from tubesentry.contracts.schemas import (
    AuditSummaryReport,
    ClassifiedChannelRecord,
    WasteCategoryBreakdown,
)
from tubesentry.contracts.taxonomy import CATEGORY_DESCRIPTIONS, WasteCategory
from tubesentry.core.heuristics import evaluate_heuristics_detailed
from tubesentry.core.seed_db import lookup_seed_channel


def normalize_topic_category(topic_str: str) -> str:
    """Extracts clean topic name from Wikipedia URL or Freebase string."""
    if "wiki/" in topic_str:
        topic_name = topic_str.split("wiki/", 1)[1]
    elif "/" in topic_str:
        topic_name = topic_str.rsplit("/", 1)[-1]
    else:
        topic_name = topic_str
    return topic_name.replace("_", " ").strip()


def run_free_audit(
    df: pd.DataFrame,
    target_languages: list[str] | None = None,
    target_cpa: float | None = None,
    print_banner: bool = True,
    currency: str = "EUR",
) -> AuditSummaryReport:
    """Executes the free diagnostic placement audit using the bundled seed DB and heuristics.

    Reveals the exact total wasted spend across all 6 risk categories, impression-weighted metrics,
    and the top 25 worst offending channels unmasked, while masking the tail behind Pro upgrade notices.
    """
    total_placements = len(df)
    total_spend = float(df["cost"].sum()) if not df.empty and "cost" in df.columns else 0.0
    total_impressions = int(df["impressions"].sum()) if not df.empty and "impressions" in df.columns else 0

    classified_records: list[ClassifiedChannelRecord] = []

    # Aggregate by unique channel_id or raw_placement to avoid duplicate rows for the same channel
    grouped = (
        df.groupby(
            ["raw_placement", "channel_id", "channel_title"],
            dropna=False,
            as_index=False,
        )
        .agg(
            {
                "cost": "sum",
                "impressions": "sum",
                "views": "sum",
                "clicks": "sum",
                "conversions": "sum",
            }
        )
        .sort_values(by="cost", ascending=False)
    )

    category_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "wasted_spend": 0.0,
            "channel_count": 0,
            "impressions": 0,
            "views": 0,
            "clicks": 0,
            "conversions": 0.0,
        }
    )

    # Accumulator for impression-weighted quality scoring (1 to 10 scale)
    total_quality_points = 0.0

    for _, row in grouped.iterrows():
        raw_pl = str(row["raw_placement"]) if pd.notna(row["raw_placement"]) else ""
        ch_id = str(row["channel_id"]) if pd.notna(row["channel_id"]) else None
        title = str(row["channel_title"]) if pd.notna(row["channel_title"]) else raw_pl
        cost = float(row["cost"])
        impr = int(row["impressions"])
        views = int(row["views"])
        clicks = int(row["clicks"])
        conv = float(row["conversions"])

        # 1. Check Seed DB
        category: str = "CLEAN"
        confidence: float = 0.0
        reason: str = "Clean"
        is_young_kids = False
        granular_sub = "CLEAN_AUDIENCE"

        if ch_id:
            seed_match = lookup_seed_channel(ch_id)
            if seed_match:
                category = seed_match["category"]
                confidence = seed_match["confidence"]
                reason = seed_match["reason"]
                if category == "MADE_FOR_KIDS":
                    is_young_kids = True
                    granular_sub = "YOUNG_KIDS_TODDLER"

        # 2. Check Open-Core Heuristics if not matched in seed
        if category == "CLEAN":
            h_res = evaluate_heuristics_detailed(
                channel_title=title,
                raw_placement=raw_pl,
                impressions=impr,
                views=views,
                clicks=clicks,
                cost=cost,
                conversions=conv,
                target_languages=target_languages,
                target_cpa=target_cpa,
            )
            if h_res["category"] != "CLEAN":
                category = h_res["category"]
                confidence = h_res["confidence"]
                reason = h_res["reason"]
                is_young_kids = h_res.get("is_young_kids", False)
                granular_sub = h_res.get("granular_sub_category", category)

        # Compute placement quality points (1.0 to 10.0 scale)
        if category == "CLEAN":
            row_quality = 10.0
        elif is_young_kids:
            row_quality = 1.0
        elif category in ("MADE_FOR_KIDS", "AI_SLOP_CLICK_FARM"):
            row_quality = 1.5
        elif category in ("PASSIVE_AUDIO_MUSIC", "FOREIGN_SCRIPT_LEAK"):
            row_quality = 2.0
        elif category == "LOW_AGE_GAMING":
            row_quality = 2.5
        else:  # PERFORMANCE_SINKHOLE
            row_quality = 3.5

        total_quality_points += row_quality * max(impr, 1)

        if category != "CLEAN":
            rec = ClassifiedChannelRecord(
                channel_id=ch_id or "UC_UNKNOWN_HANDLE",
                channel_title=title,
                waste_category=category,  # type: ignore[arg-type]
                waste_confidence=round(confidence, 2),
                made_for_kids_official=(category == "MADE_FOR_KIDS"),
                is_young_kids=is_young_kids,
                granular_sub_category=granular_sub,
                thumbnail_url=None,
                detected_language=None,
                detected_country=None,
                topic_categories=[],
                cost=round(cost, 2),
                impressions=impr,
                views=views,
                clicks=clicks,
                conversions=round(conv, 2),
                reason_summary=reason,
                is_masked=False,
            )
            classified_records.append(rec)

            stats = category_stats[category]
            stats["wasted_spend"] += cost
            stats["channel_count"] += 1
            stats["impressions"] += impr
            stats["views"] += views
            stats["clicks"] += clicks
            stats["conversions"] += conv

    # Sort offending channels descending by wasted cost
    classified_records.sort(key=lambda x: x.cost, reverse=True)

    total_wasted_spend = sum(stats["wasted_spend"] for stats in category_stats.values())
    waste_percentage = (total_wasted_spend / total_spend * 100.0) if total_spend > 0 else 0.0
    total_waste_channels = len(classified_records)

    total_wasted_impressions = sum(stats["impressions"] for stats in category_stats.values())
    wasted_impressions_percentage = (
        (total_wasted_impressions / total_impressions * 100.0) if total_impressions > 0 else 0.0
    )

    weight_denom = max(total_impressions, len(grouped))
    weighted_quality_score = round(total_quality_points / weight_denom, 1) if weight_denom > 0 else 10.0
    weighted_quality_score = max(1.0, min(10.0, weighted_quality_score))

    # Free Tier Masking Invariant:
    # First 25 channels are completely unmasked.
    # Channels 26+ are masked with UC•••••••••••• and locked placeholder title.
    top_offenders: list[ClassifiedChannelRecord] = []
    masked_count = 0

    for idx, rec in enumerate(classified_records):
        if idx < 25:
            top_offenders.append(rec)
        else:
            masked_count += 1
            top_offenders.append(
                rec.model_copy(
                    update={
                        "channel_id": "UC••••••••••••",
                        "channel_title": "[LOCKED IN FREE TIER — Upgrade to TubeSentry Pro]",
                        "is_masked": True,
                    }
                )
            )

    breakdowns: dict[str, WasteCategoryBreakdown] = {}
    for cat_enum in WasteCategory:
        cat_key = cat_enum.value
        if cat_key == "CLEAN":
            continue
        stats = category_stats[cat_key]
        spend_pct = (stats["wasted_spend"] / total_spend * 100.0) if total_spend > 0 else 0.0
        breakdowns[cat_key] = WasteCategoryBreakdown(
            category=cat_key,  # type: ignore[arg-type]
            wasted_spend=round(stats["wasted_spend"], 2),
            wasted_spend_percentage=round(spend_pct, 2),
            channel_count=int(stats["channel_count"]),
            impressions=int(stats["impressions"]),
            views=int(stats["views"]),
            clicks=int(stats["clicks"]),
            conversions=round(stats["conversions"], 2),
            description=CATEGORY_DESCRIPTIONS.get(cat_enum, ""),
        )

    coppa_kids_spend = category_stats["MADE_FOR_KIDS"]["wasted_spend"]
    annual_runrate = total_wasted_spend * 12.0

    banner_text = _build_diagnostic_banner(
        total_placements=total_placements,
        total_spend=total_spend,
        total_wasted_spend=total_wasted_spend,
        waste_percentage=waste_percentage,
        total_waste_channels=total_waste_channels,
        total_impressions=total_impressions,
        total_wasted_impressions=total_wasted_impressions,
        wasted_impressions_percentage=wasted_impressions_percentage,
        weighted_quality_score=weighted_quality_score,
        breakdowns=breakdowns,
        masked_count=masked_count,
        currency=currency,
    )

    if print_banner:
        console = Console(stderr=False)
        console.print(banner_text)

    return AuditSummaryReport(
        total_placements_audited=total_placements,
        total_spend=round(total_spend, 2),
        total_wasted_spend=round(total_wasted_spend, 2),
        wasted_spend_percentage=round(waste_percentage, 2),
        total_waste_channels=total_waste_channels,
        total_impressions_audited=total_impressions,
        total_wasted_impressions=total_wasted_impressions,
        wasted_impressions_percentage=round(wasted_impressions_percentage, 2),
        weighted_quality_score=round(weighted_quality_score, 1),
        top_topic_categories=[],
        currency_code=currency,
        category_breakdowns=breakdowns,
        top_offenders=top_offenders,
        masked_offenders_count=masked_count,
        is_pro_audit=False,
        coppa_kids_risk_spend=round(coppa_kids_spend, 2),
        annualized_recoverable_runrate=round(annual_runrate, 2),
        upgrade_prompt=banner_text,
    )


def _build_diagnostic_banner(
    total_placements: int,
    total_spend: float,
    total_wasted_spend: float,
    waste_percentage: float,
    total_waste_channels: int,
    total_impressions: int,
    total_wasted_impressions: int,
    wasted_impressions_percentage: float,
    weighted_quality_score: float,
    breakdowns: dict[str, WasteCategoryBreakdown],
    masked_count: int,
    currency: str = "EUR",
) -> str:
    """Constructs the Rich upgrade diagnostic banner string matching spec Section 4.1."""
    sym = "€" if currency == "EUR" else ("$" if currency == "USD" else currency)

    lines = [
        "=" * 84,
        " TUBESENTRY OPEN-CORE v0.1.0 — YOUTUBE PLACEMENT WASTE DIAGNOSTIC",
        "=" * 84,
        f" Audited Placements:        {total_placements:,} placements | Total Spend: {sym} {total_spend:,.2f}",
        f" Identified Wasted Spend:   {sym} {total_wasted_spend:,.2f} ({waste_percentage:.1f}% of budget) across {total_waste_channels:,} channels",
        f" Impression Waste Impact:   {total_wasted_impressions:,} imps ({wasted_impressions_percentage:.1f}% wasted) | Placement Quality: {weighted_quality_score:.1f}/10",
        "-" * 84,
        " [!] WASTED BUDGET BY CATEGORY:",
    ]

    # Sort categories by wasted spend descending
    sorted_cats = sorted(breakdowns.values(), key=lambda b: b.wasted_spend, reverse=True)
    idx = 1
    category_labels = {
        "MADE_FOR_KIDS": "COPPA / Toddler",
        "PASSIVE_AUDIO_MUSIC": "Lofi / Sleep / BG",
        "FOREIGN_SCRIPT_LEAK": "Cyrillic / Arabic / Asian",
        "LOW_AGE_GAMING": "Roblox / Minecraft",
        "AI_SLOP_CLICK_FARM": "Faceless AI / Slop",
        "PERFORMANCE_SINKHOLE": "High CPA / 0 Conv",
    }

    for b in sorted_cats:
        if b.wasted_spend > 0:
            label = category_labels.get(b.category, "")
            lines.append(
                f" {idx}. [{b.category:<20}]  {sym} {b.wasted_spend:>10,.2f} ({b.wasted_spend_percentage:>4.1f}%) — {b.channel_count:>5,} channels ({label})"
            )
            idx += 1

    lines.extend(
        [
            "-" * 84,
            " [!] FREE TIER EXPORT LIMIT:",
            f" Showing Top 25 worst offending channels below. {masked_count:,} additional waste channels are",
            " masked (`UC••••••••••••`).",
            "",
            f" [*] Unlock All {total_waste_channels:,} Flagged Channels, 65k Google Ads Exclusion CSV & HTML Deck:",
            "    >>> tubesentry auth --key TS_PRO_...",
            "    Get an instant Single Audit Pass (€199) or Agency License: https://tubesentry.dev",
            "=" * 84,
        ]
    )
    return "\n".join(lines)
