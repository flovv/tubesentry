from __future__ import annotations

from enum import Enum


class WasteCategory(str, Enum):
    """Canonical 6-Vector Waste Taxonomy for YouTube Placement Audits."""
    CLEAN = "CLEAN"
    MADE_FOR_KIDS = "MADE_FOR_KIDS"
    PASSIVE_AUDIO_MUSIC = "PASSIVE_AUDIO_MUSIC"
    LOW_AGE_GAMING = "LOW_AGE_GAMING"
    FOREIGN_SCRIPT_LEAK = "FOREIGN_SCRIPT_LEAK"
    AI_SLOP_CLICK_FARM = "AI_SLOP_CLICK_FARM"
    PERFORMANCE_SINKHOLE = "PERFORMANCE_SINKHOLE"


# Freebase topic IDs and Wikipedia ontology mappings from YouTube Data API v3
FREEBASE_TOPIC_MAPPINGS = {
    # Music topics
    "/m/04rlf": "Music",
    "/m/02mscn": "Christian music",
    "/m/0ggq0m": "Classical music",
    "/m/01lyv": "Country",
    "/m/02lkt": "Electronic music",
    "/m/0g293": "Music of Latin America",
    "/m/064t9": "Pop music",
    "/m/06cq9": "Reggae",
    "/m/06j6l": "Rhythm and blues",
    "/m/06by7": "Rock music",
    "/m/0gywn": "Soul music",
    "/m/0zdp4": "Hip hop music",
    # Gaming topics
    "/m/0bzvm2": "Gaming",
    "/m/025zzc": "Action game",
    "/m/02ntfj": "Action-adventure game",
    "/m/0b1vjn": "Casual game",
    "/m/0403hg": "Role-playing video game",
    "/m/02hygl": "Simulation video game",
    "/m/04q1x3q": "Sports game",
    "/m/01sjng": "Strategy video game",
    # Children & Animation topics
    "/m/0164x2": "Children's music",
    "/m/03k3r": "Animated cartoon",
    "/m/019_rr": "Lifestyle",
    "/m/028sqc": "Music of Asia",
}

# Bitmask constants for compressed 250k registry
BITMASK_MUSIC = 1 << 0
BITMASK_GAMING = 1 << 1
BITMASK_KIDS = 1 << 2
BITMASK_ANIMATION = 1 << 3
BITMASK_ENTERTAINMENT = 1 << 4
BITMASK_EDUCATION = 1 << 5
BITMASK_NEWS = 1 << 6
BITMASK_LIFESTYLE = 1 << 7

CATEGORY_DESCRIPTIONS: dict[WasteCategory, str] = {
    WasteCategory.CLEAN: "Verified clean audience placement with standard engagement.",
    WasteCategory.MADE_FOR_KIDS: "Toddler & COPPA nursery rhymes, unboxing, cartoons, and child-directed channels.",
    WasteCategory.PASSIVE_AUDIO_MUSIC: "Background audio, lofi beats, sleep music, rain noise, and zero-attention streams.",
    WasteCategory.LOW_AGE_GAMING: "Underage gameplay (Roblox, Minecraft, Brawl Stars, Skibidi, Gacha) with accidental child taps.",
    WasteCategory.FOREIGN_SCRIPT_LEAK: "Foreign language and non-Latin script leakage mismatched with campaign geotargeting.",
    WasteCategory.AI_SLOP_CLICK_FARM: "High-frequency synthetic AI content farms, faceless TTS shorts, and click arbitrage.",
    WasteCategory.PERFORMANCE_SINKHOLE: "Empirical budget bleed placements exceeding 3x Target CPA with zero conversions.",
}
