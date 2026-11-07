from __future__ import annotations


def generate_bigquery_dts_sql(
    dataset: str = "google_ads_export",
    table_prefix: str = "p_Placement_",
    customer_id: str = "",
    lookback_days: int = 30,
    target_cpa: float | None = 40.0,
    as_dbt: bool = False,
) -> str:
    """Generates an optimized BigQuery SQL model/script to audit YouTube and PMax placement reports

    directly from Google Ads Data Transfer Service (DTS) raw tables.

    Compatible with standard Google Ads BigQuery DTS schemas:
      - `p_Placement_<customer_id>`
      - `ads_Placement_<customer_id>`

    Args:
        dataset: BigQuery dataset name (e.g. 'google_ads_data' or 'dbt_ads').
        table_prefix: Table prefix from Google Ads DTS (default: 'p_Placement_').
        customer_id: Optional Google Ads Customer ID suffix (e.g. '1234567890').
        lookback_days: Date lookback filter in days (default: 30).
        target_cpa: Target CPA in account currency for identifying performance sinkholes.
        as_dbt: If True, formats as a dbt model with Jinja `{{ config(...) }}` and source macros.

    Returns:
        str: Production-grade BigQuery Standard SQL query.
    """
    table_name = f"`{dataset}.{table_prefix}{customer_id}`" if customer_id else f"`{dataset}.{table_prefix}*`"
    cpa_threshold = target_cpa if target_cpa is not None else 40.0

    dbt_header = """{{ config(
    materialized = 'table',
    partition_by = {
      'field': 'audit_date',
      'data_type': 'date'
    },
    cluster_by = ['waste_category', 'channel_id']
) }}

""" if as_dbt else ""

    sql = f"""{dbt_header}-- TubeSentry BigQuery DTS Placement Waste Auditor
-- Generated automatically by TubeSentry (https://github.com/flovv/tubesentry)
-- Evaluates YouTube and Performance Max placements in Google Ads Data Transfer Service (DTS)

WITH raw_placements AS (
  SELECT
    _DATA_DATE AS audit_date,
    campaign_id,
    campaign_name,
    ad_group_id,
    ad_group_name,
    placement_url,
    display_name AS channel_title,
    metrics_impressions AS impressions,
    metrics_views AS views,
    metrics_clicks AS clicks,
    (metrics_cost_micros / 1000000.0) AS cost,
    metrics_conversions AS conversions,
    (metrics_conversions_value_in_local_currency) AS conversion_value,
    -- Extract 24-character YouTube Channel ID (UC...) if present
    REGEXP_EXTRACT(placement_url, r'(UC[a-zA-Z0-9_-]{{22}})') AS channel_id
  FROM {table_name}
  WHERE
    _DATA_DATE >= DATE_SUB(CURRENT_DATE(), INTERVAL {lookback_days} DAY)
    AND placement_url LIKE '%youtube.com%'
),

scored_placements AS (
  SELECT
    audit_date,
    campaign_id,
    campaign_name,
    ad_group_id,
    ad_group_name,
    placement_url,
    channel_id,
    channel_title,
    impressions,
    views,
    clicks,
    cost,
    conversions,
    conversion_value,
    SAFE_DIVIDE(cost, conversions) AS cpa,
    SAFE_DIVIDE(clicks, impressions) AS ctr,

    -- 1. Heuristic Risk Flags
    -- A. Made-for-Kids & Toddler Nursery Rhymes
    REGEXP_CONTAINS(
      LOWER(CONCAT(IFNULL(channel_title, ''), ' ', IFNULL(placement_url, ''))),
      r'(cocomelon|chuchu|looloo|nursery|rhymes|lullab|kids|kinder|toddler|baby|sing-along|cartoons|super joey|peppa|bebefinn|diana and roma|vlad and niki|wolfoo)'
    ) AS is_made_for_kids,

    -- B. Passive Audio & Sleep Streams
    REGEXP_CONTAINS(
      LOWER(CONCAT(IFNULL(channel_title, ''), ' ', IFNULL(placement_url, ''))),
      r'(lofi|chillhop|relaxing music|sleep music|sleep sounds|rain sounds|ambient sound|white noise|binaural|meditation beats|study music|instrumental worship)'
    ) AS is_passive_music,

    -- C. Underage Sandbox Gaming
    REGEXP_CONTAINS(
      LOWER(CONCAT(IFNULL(channel_title, ''), ' ', IFNULL(placement_url, ''))),
      r'(roblox|minecraft|brawl stars|skibidi|geometry dash|fortnite funny|gacha life|adopt me|brookhaven|blox fruits)'
    ) AS is_underage_gaming,

    -- D. Foreign Non-Latin Script Mismatches (Cyrillic, Arabic, Devanagari, Thai, CJK)
    REGEXP_CONTAINS(
      IFNULL(channel_title, ''),
      r'[\\p{{Cyrillic}}\\p{{Arabic}}\\p{{Devanagari}}\\p{{Thai}}\\p{{Han}}\\p{{Hiragana}}\\p{{Katakana}}\\p{{Hangul}}]'
    ) AS is_foreign_script,

    -- E. Performance Sinkhole (> 3x Target CPA without conversions)
    (cost >= {cpa_threshold * 3.0} AND (conversions IS NULL OR conversions = 0)) AS is_performance_sinkhole

  FROM raw_placements
),

classified_summary AS (
  SELECT
    *,
    CASE
      WHEN is_made_for_kids THEN 'MADE_FOR_KIDS'
      WHEN is_passive_music THEN 'PASSIVE_AUDIO_MUSIC'
      WHEN is_underage_gaming THEN 'LOW_AGE_GAMING'
      WHEN is_foreign_script THEN 'FOREIGN_SCRIPT_LEAK'
      WHEN is_performance_sinkhole THEN 'PERFORMANCE_SINKHOLE'
      ELSE 'CLEAN'
    END AS waste_category,

    CASE
      WHEN is_made_for_kids THEN 1.0
      WHEN is_passive_music OR is_foreign_script THEN 2.0
      WHEN is_underage_gaming THEN 2.5
      WHEN is_performance_sinkhole THEN 3.5
      ELSE 10.0
    END AS quality_score,

    CASE
      WHEN is_made_for_kids OR is_passive_music OR is_underage_gaming OR is_foreign_script OR is_performance_sinkhole
      THEN cost
      ELSE 0.0
    END AS wasted_cost,

    CASE
      WHEN is_made_for_kids OR is_passive_music OR is_underage_gaming OR is_foreign_script OR is_performance_sinkhole
      THEN impressions
      ELSE 0
    END AS wasted_impressions,

    -- Exclusion URL formatted for Google Ads Editor / AdsApp scripts
    CASE
      WHEN channel_id IS NOT NULL THEN CONCAT('youtube.com/channel/', channel_id)
      ELSE placement_url
    END AS formatted_exclusion_url

  FROM scored_placements
)

SELECT
  audit_date,
  campaign_id,
  campaign_name,
  channel_id,
  channel_title,
  formatted_exclusion_url,
  waste_category,
  quality_score,
  impressions,
  views,
  clicks,
  cost,
  conversions,
  wasted_cost,
  wasted_impressions,
  is_made_for_kids,
  is_passive_music,
  is_underage_gaming,
  is_foreign_script,
  is_performance_sinkhole
FROM classified_summary
WHERE waste_category != 'CLEAN'
ORDER BY wasted_cost DESC;
"""
    return sql
