from __future__ import annotations

import re
import unicodedata
from typing import Any

# Compiled regexes for high-performance vectorized evaluation
YOUNG_KIDS_REGEX = re.compile(
    r"(?i)\b(cocomelon|bebefinn|chuchu\s*tv|peppa\s*pig|super\s*simple\s*songs|"
    r"little\s*baby\s*bum|pinkfong|baby\s*shark|vlad\s*and\s*niki|diana\s*and\s*roma|"
    r"nursery\s*rhymes?|kinderlieder|canciones\s*infantiles|comptines|canzoni\s*per\s*bambini|"
    r"el\s*reino\s*infantil|gallina\s*pintadita|toy\s*unboxing|learn\s*colors|alphabet\s*song|"
    r"toddler|kindergarten|sing-along|lullaby|schlaflied|baby\s*songs?)\b"
)

KIDS_REGEX = re.compile(
    r"(?i)\b(nursery\s*rhymes?|kinderlieder|canciones\s*infantiles|comptines|"
    r"canzoni\s*per\s*bambini|cocomelon|bebefinn|chuchu\s*tv|peppa\s*pig|"
    r"paw\s*patrol|blippi|super\s*simple\s*songs|little\s*baby\s*bum|pinkfong|"
    r"baby\s*shark|vlad\s*and\s*niki|diana\s*and\s*roma|el\s*reino\s*infantil|"
    r"gallina\s*pintadita|toy\s*unboxing|learn\s*colors|alphabet\s*song|"
    r"toddler|kindergarten|sing-along|lullaby|schlaflied|baby\s*songs?)\b"
)

PASSIVE_MUSIC_REGEX = re.compile(
    r"(?i)\b(lofi|lo-fi|relaxing\s*music|sleep\s*music|rain\s*sounds|white\s*noise|"
    r"study\s*beats|ambient\s*music|meditation\s*music|healing\s*frequency|432\s*hz|"
    r"528\s*hz|10\s*hours|8\s*hours|karaoke|instrumental\s*mix|deep\s*focus|"
    r"coffee\s*shop\s*jazz|schlafmusik|música\s*para\s*dormir)\b"
)

LOW_AGE_GAMING_REGEX = re.compile(
    r"(?i)\b(roblox|brookhaven|blox\s*fruits|minecraft\s*pe|brawl\s*stars|gacha\s*life|"
    r"gacha\s*club|skibidi\s*toilet|fnf|friday\s*night\s*funkin|among\s*us\s*animation|"
    r"subway\s*surfers|stumble\s*guys|pk\s*xd|toca\s*life|toca\s*boca|geometry\s*dash)\b"
)

AI_SLOP_REGEX = re.compile(
    r"(?i)\b(reddit\s*stories|aita\s*stories|ai\s*facts|satisfying\s*slime|"
    r"hydraulic\s*press\s*shorts|family\s*guy\s*clips|subway\s*surfers\s*reddit)\b"
)

# Unicode non-Latin script ranges:
# Cyrillic: \u0400-\u04FF
# Arabic: \u0600-\u06FF
# Devanagari (Hindi): \u0900-\u097F
# Bengali: \u0980-\u09FF
# Thai: \u0E00-\u0E7F
# Hangul: \uAC00-\uD7AF, \u1100-\u11FF
# CJK: \u4E00-\u9FFF, \u3400-\u4DBF
NON_LATIN_SCRIPT_PATTERN = re.compile(
    r"[\u0400-\u04FF\u0600-\u06FF\u0900-\u097F\u0980-\u09FF\u0E00-\u0E7F"
    r"\uAC00-\uD7AF\u1100-\u11FF\u4E00-\u9FFF\u3400-\u4DBF]"
)


def compute_non_latin_ratio(text: str) -> float:
    """Computes the ratio of non-Latin script characters to total alphabetic letters.

    Returns float in [0.0, 1.0].
    """
    if not text:
        return 0.0

    total_letters = 0
    non_latin_letters = 0

    for char in text:
        if unicodedata.category(char).startswith("L"):
            total_letters += 1
            if NON_LATIN_SCRIPT_PATTERN.match(char):
                non_latin_letters += 1

    if total_letters == 0:
        return 0.0
    return non_latin_letters / total_letters


def is_young_kids_text(text: str) -> bool:
    """Checks if text specifically targets toddlers / under 10 (nursery rhymes, CoCoMelon, etc.)."""
    return bool(YOUNG_KIDS_REGEX.search(text)) if text else False


def is_made_for_kids_text(text: str) -> bool:
    """Checks if text contains toddler or Made-for-Kids keywords."""
    return bool(KIDS_REGEX.search(text)) if text else False


def is_passive_music_text(text: str) -> bool:
    """Checks if text contains passive audio / background music keywords."""
    if not text:
        return False
    if text.endswith((" - Topic", "VEVO", " VEVO")):
        return True
    return bool(PASSIVE_MUSIC_REGEX.search(text))


def is_low_age_gaming_text(text: str) -> bool:
    """Checks if text contains underage gaming keywords."""
    return bool(LOW_AGE_GAMING_REGEX.search(text)) if text else False


def is_ai_slop_text(text: str) -> bool:
    """Checks if text contains faceless AI slop keywords."""
    return bool(AI_SLOP_REGEX.search(text)) if text else False


def evaluate_heuristics_detailed(
    channel_title: str,
    raw_placement: str = "",
    impressions: int = 0,
    views: int = 0,
    clicks: int = 0,
    cost: float = 0.0,
    conversions: float = 0.0,
    target_languages: list[str] | None = None,
    target_cpa: float | None = None,
) -> dict[str, Any]:
    """Evaluates placement heuristics with granular sub-category and toddler detection.

    Returns dict with keys:
        category, confidence, reason, is_young_kids, granular_sub_category
    """
    [lang.lower()[:2] for lang in (target_languages or ["de", "en"])]
    combined_text = f"{channel_title} {raw_placement}"

    # Rule 1: MADE_FOR_KIDS & YOUNG_KIDS
    if is_made_for_kids_text(combined_text):
        young = is_young_kids_text(combined_text)
        sub_cat = "YOUNG_KIDS_TODDLER" if young else "GENERAL_KIDS_CARTOON"
        reason = (
            "Matched toddler / under-10 nursery rhyme & brainrot lexicon."
            if young
            else "Matched Made-for-Kids toddler/nursery rhyme lexicon."
        )
        return {
            "category": "MADE_FOR_KIDS",
            "confidence": 0.95 if young else 0.92,
            "reason": reason,
            "is_young_kids": young,
            "granular_sub_category": sub_cat,
        }

    # Rule 2: PASSIVE_AUDIO_MUSIC
    if is_passive_music_text(channel_title):
        return {
            "category": "PASSIVE_AUDIO_MUSIC",
            "confidence": 0.90,
            "reason": "Matched passive audio/background music streams.",
            "is_young_kids": False,
            "granular_sub_category": "PASSIVE_AUDIO_STREAM",
        }

    # Rule 3: LOW_AGE_GAMING
    if is_low_age_gaming_text(combined_text):
        return {
            "category": "LOW_AGE_GAMING",
            "confidence": 0.85,
            "reason": "Matched underage gaming franchise lexicon (Roblox/Minecraft/etc.).",
            "is_young_kids": False,
            "granular_sub_category": "LOW_AGE_GAMING_SINK",
        }

    # Rule 4: FOREIGN_SCRIPT_LEAK
    ratio = compute_non_latin_ratio(channel_title)
    if ratio >= 0.25:
        return {
            "category": "FOREIGN_SCRIPT_LEAK",
            "confidence": 0.95,
            "reason": f"Non-Latin script ratio {ratio:.1%} in title (Cyrillic/Arabic/Asian scripts).",
            "is_young_kids": False,
            "granular_sub_category": "GEO_LANGUAGE_LEAK",
        }

    # Rule 5: AI_SLOP_CLICK_FARM
    if is_ai_slop_text(combined_text) and conversions == 0:
        return {
            "category": "AI_SLOP_CLICK_FARM",
            "confidence": 0.82,
            "reason": "Matched faceless AI content lexicon with 0 conversions.",
            "is_young_kids": False,
            "granular_sub_category": "AI_SLOP_FARM",
        }

    # Rule 6: PERFORMANCE_SINKHOLE
    vtr = (views / max(impressions, 1)) if impressions > 0 else 0.0
    if (
        target_cpa is not None
        and target_cpa > 0
        and cost >= 3.0 * target_cpa
        and conversions == 0
        and vtr < 0.15
    ):
        return {
            "category": "PERFORMANCE_SINKHOLE",
            "confidence": 0.80,
            "reason": f"Placement spend (€{cost:.2f}) >= 3x target CPA (€{target_cpa:.2f}) with 0 conv and VTR {vtr:.1%}.",
            "is_young_kids": False,
            "granular_sub_category": "HIGH_CPA_SINKHOLE",
        }

    return {
        "category": "CLEAN",
        "confidence": 0.0,
        "reason": "No waste patterns detected.",
        "is_young_kids": False,
        "granular_sub_category": "CLEAN_AUDIENCE",
    }


def evaluate_heuristics(
    channel_title: str,
    raw_placement: str = "",
    impressions: int = 0,
    views: int = 0,
    clicks: int = 0,
    cost: float = 0.0,
    conversions: float = 0.0,
    target_languages: list[str] | None = None,
    target_cpa: float | None = None,
) -> tuple[str, float, str]:
    """Applies open-core deterministic heuristic rules to evaluate placement waste.

    Returns:
        tuple[waste_category, confidence, reason_summary]
    """
    res = evaluate_heuristics_detailed(
        channel_title=channel_title,
        raw_placement=raw_placement,
        impressions=impressions,
        views=views,
        clicks=clicks,
        cost=cost,
        conversions=conversions,
        target_languages=target_languages,
        target_cpa=target_cpa,
    )
    return (res["category"], res["confidence"], res["reason"])
