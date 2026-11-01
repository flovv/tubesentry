from __future__ import annotations

import csv
import random
from pathlib import Path

# Representative channel templates for synthetic generation
_CLEAN_CHANNELS = [
    ("UCBJycsmduvYEL83R_U4JriQ", "Marques Brownlee - Tech Reviews"),
    ("UCsXVk37bltHxD1rDPwtNM8Q", "Kurzgesagt – In a Nutshell"),
    ("UCsooa4yRKGN_zEE8iknghZA", "TED-Ed Educational Lessons"),
    ("UC4QZ_LsYcvcq7qOsOhpAX4A", "ColdFusion Modern Technology"),
    ("UC0intLFzLaudFG-xAvUEAwA", "Veritasium - Science & Wonder"),
    ("UC7_gcs09iThXybpVgjHZ_7g", "PBS Space Time Astrophysics"),
    ("UCv_vLHiWPYh_535Ex9jVEVQ", "SmarterEveryDay Engineering"),
    ("UC6107grRI4m032ZKaxNOYfA", "NPR Tiny Desk Concerts Live"),
    ("UC9-y-6csu5WGm29I7JiwpnA", "Computerphile Programming"),
    ("UC2C_jShtL725hvbm1arSV9w", "CGP Grey Explanations"),
]

_KIDS_CHANNELS = [
    ("UCbCmjCuTUZos6Inko4u57UQ", "Cocomelon - Nursery Rhymes"),
    ("UCX6OQ3DkcsbYNE6H8uQQuVA", "Pinkfong Baby Shark - Kids Songs"),
    ("UCvlE5gTbOvjiolFlEm-c_Ow", "Vlad and Niki Toddler Toys"),
    ("UCk8GzjMOrta8yxDcKfylJYw", "Kids Diana Show Playtime"),
    ("UCBnZ16ahKA2DZ_T5W0FPUXg", "ChuChu TV Nursery Rhymes Kids"),
    ("UC_hS448D-Jd80fXgKx-3p0w", "Bebefinn - Nursery Rhymes 3D"),
    ("UC4NALVCmcmL5ntpV0thoH6w", "Peppa Pig Official Channel"),
    ("UC1f0_a7JqLq4M9gX-a2X8Lw", "Sing mit mir - Kinderlieder Deutsch"),
    ("UCbmT_5p1XmZ3Nl9wXhB9xQw", "El Reino Infantil Canciones"),
    ("UC5UtK8v_XGqV9k_L5v7H83w", "Blippi - Educational Videos for Kids"),
]

_MUSIC_CHANNELS = [
    ("UCSJ4gkVC6NrvII8umztf0Ow", "Lofi Girl 24/7 Study Beats"),
    ("UCOxqgCwgOq3EW3873G5gHyw", "Chillhop Music Chill Beats"),
    ("UCz7X3N8lC0Vw2xU4q8h6t-Q", "Yellow Brick Cinema - Relaxing Sleep Music"),
    ("UCyD07A1eG2YQ3q3M0A4M8tQ", "Soothing Relaxation Ambient 8 Hours"),
    ("UC7tX2u9g9y0hZ5j1l2m3n-Q", "Cafe Music BGM channel Coffee Jazz"),
    ("UC8uY3v0h0z1j2k3l4m5n-Pw", "Rain Sounds 10 Hours Deep Sleep"),
    ("UC1xY6z3k3z4k5l6m7n8o-Sw", "Meditative Mind 432Hz Chakra Frequency"),
    ("UC9vW4x1i1z2k3l4m5n6o-Qw", "Deep Focus Binaural Beats Study"),
]

_GAMING_CHANNELS = [
    ("UCv8u_4yZ6vX9_1m2n3o4p-Q", "Aphmau - Underage Roblox Roleplay"),
    ("UCzO3y1m4p4x1_6a2N-4L_Pw", "PrestonPlayz - Roblox Extreme Challenge"),
    ("UCcD3_4e5F6g7_8h9I0j1K-Q", "Skibidi Toilet Multiverse Episode"),
    ("UCbC2_3d4E5f6_7g8H9i0J-Q", "Gacha Life Mini Movie Sad Story"),
    ("UCdE4_5f6G7h8_9i0J1k2L-Q", "Subway Surfers Gameplay High Score"),
    ("UCeF5_6g7H8i9_0j1K2l3M-Q", "Stumble Guys Funny Moments"),
]

_FOREIGN_CHANNELS = [
    ("UCq-GFYZe9K9_mQG9F_1QZow", "T-Series Hindi Bollywood Music"),
    ("UC0r8_9m1N2o3_4p5Q6r7S-Q", "Маша и Медведь Мультики для детей"),
    ("UC1s9_0n2O3p4_5q6R7s8T-Q", "Toyor Al Janah طيور الجنة للأطفال"),
    ("UC2t0_1o3P4q5_6r7S8t9U-Q", "ช่อง one31 ละครไทยเต็มเรื่อง"),
    ("UC5w3_4r6S7t8_9u0V1w2X-Q", "Вечерний Ургант Русское Шоу"),
    ("UC3u1_2p4Q5r6_7s8T9u0V-Q", "مسلسلات رمضان قناة إم بي سي"),
]

_AI_SLOP_CHANNELS = [
    ("UC7y5_6t8U9v0_1w2X3y4Z-Q", "Reddit Stories Daily Text-to-Speech Shorts"),
    ("UC8z6_7u9V0w1_2x3Y4z5A-Q", "Satisfying Slime ASMR Kinetic Sand Cuts"),
    ("UC9a7_8v0W1x2_3y4Z5a6B-Q", "Hydraulic Press Shorts Glowing Knife"),
    ("UC0b8_9w1X2y3_4z5A6b7C-Q", "Dark Psychology AI Facts Quotes Shorts"),
    ("UC1c9_0x2Y3z4_5a6B7c8D-Q", "Family Guy Clips Subway Surfers Reddit Split"),
]


def generate_synthetic_placement_csv(
    output_path: str | Path,
    num_rows: int = 25000,
    seed: int = 42,
    language: str = "de",
) -> Path:
    """Generates a realistic Google Ads / DV360 placement CSV report with known waste proportions."""
    rng = random.Random(seed)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Weights: 65% Clean, 14% Kids, 10% Music, 5% Gaming, 4% Foreign, 2% AI Slop
    categories = [
        (_CLEAN_CHANNELS, 0.65),
        (_KIDS_CHANNELS, 0.14),
        (_MUSIC_CHANNELS, 0.10),
        (_GAMING_CHANNELS, 0.05),
        (_FOREIGN_CHANNELS, 0.04),
        (_AI_SLOP_CHANNELS, 0.02),
    ]

    header_cols = [
        "Placement",
        "Placement name",
        "Cost",
        "Impr.",
        "Views",
        "Clicks",
        "Conversions",
    ]

    lines: list[list[str]] = []

    # Metadata title lines as typical in Google Ads
    lines.append(["Where ads showed report - YouTube & Display Placements"])
    lines.append(["All time / Last 30 days"])
    lines.append([])  # Blank spacer line
    lines.append(header_cols)

    total_cost = 0.0
    total_impr = 0
    total_views = 0
    total_clicks = 0
    total_conv = 0.0

    for i in range(num_rows):
        r = rng.random()
        cumulative = 0.0
        chosen_pool = _CLEAN_CHANNELS
        for pool, weight in categories:
            cumulative += weight
            if r <= cumulative:
                chosen_pool = pool
                break

        base_ch_id, base_title = rng.choice(chosen_pool)
        # Create subtle variants for long-tail placement URLs
        if rng.random() < 0.20:
            placement_url = f"https://www.youtube.com/channel/{base_ch_id}"
        elif rng.random() < 0.40:
            placement_url = f"youtube.com/channel/{base_ch_id}"
        else:
            placement_url = f"youtube.com/channel/{base_ch_id}"

        title = f"{base_title} (ID #{i % 300 + 1})"

        # Generate realistic metrics
        # Offending channels often get huge impressions, high cost, low or 0 conversions
        is_clean = chosen_pool is _CLEAN_CHANNELS
        if is_clean:
            impr = rng.randint(50, 4000)
            views = int(impr * rng.uniform(0.18, 0.45))
            clicks = int(impr * rng.uniform(0.008, 0.035))
            cost = round(impr * rng.uniform(0.015, 0.04), 2)
            conv = round(clicks * rng.uniform(0.02, 0.12), 1) if clicks > 0 else 0.0
        else:
            impr = rng.randint(200, 8000)
            views = int(impr * rng.uniform(0.05, 0.25))
            clicks = int(impr * rng.uniform(0.01, 0.06))
            cost = round(impr * rng.uniform(0.02, 0.055), 2)
            conv = 0.0 if rng.random() < 0.94 else 1.0  # Vast majority 0 conversions

        total_cost += cost
        total_impr += impr
        total_views += views
        total_clicks += clicks
        total_conv += conv

        # Format numbers (support localized formatting)
        if language == "de":
            cost_str = f"{cost:.2f} €".replace(".", ",")
            impr_str = f"{impr}"
            views_str = f"{views}"
            clicks_str = f"{clicks}"
            conv_str = f"{conv:.1f}".replace(".", ",")
        else:
            cost_str = f"${cost:.2f}"
            impr_str = f"{impr}"
            views_str = f"{views}"
            clicks_str = f"{clicks}"
            conv_str = f"{conv:.1f}"

        lines.append([placement_url, title, cost_str, impr_str, views_str, clicks_str, conv_str])

    # Footer total line
    if language == "de":
        lines.append([
            "Gesamt: Konto",
            "--",
            f"{total_cost:.2f} €".replace(".", ","),
            str(total_impr),
            str(total_views),
            str(total_clicks),
            f"{total_conv:.1f}".replace(".", ","),
        ])
    else:
        lines.append([
            "Total: Account",
            "--",
            f"${total_cost:.2f}",
            str(total_impr),
            str(total_views),
            str(total_clicks),
            f"{total_conv:.1f}",
        ])

    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(lines)

    return path
