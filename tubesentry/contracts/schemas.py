from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

WasteCategoryType = Literal[
    "CLEAN",
    "MADE_FOR_KIDS",
    "PASSIVE_AUDIO_MUSIC",
    "LOW_AGE_GAMING",
    "FOREIGN_SCRIPT_LEAK",
    "AI_SLOP_CLICK_FARM",
    "PERFORMANCE_SINKHOLE",
]


class StandardizedPlacementRow(BaseModel):
    """Normalized row extracted from Google Ads or DV360 placement report."""
    raw_placement: str = Field(..., description="Original placement URL or string from CSV")
    channel_id: str | None = Field(default=None, pattern=r"^UC[a-zA-Z0-9_-]{22}$")
    handle_or_video_id: str | None = Field(default=None)
    channel_title: str | None = Field(default=None)
    placement_type: str = Field(default="YouTube channel")
    impressions: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    cost: float = Field(default=0.0, ge=0.0)
    conversions: float = Field(default=0.0, ge=0.0)
    currency_code: str = Field(default="EUR")


class ClassifiedChannelRecord(BaseModel):
    """Enriched and scored YouTube channel record."""
    channel_id: str
    channel_title: str
    waste_category: WasteCategoryType
    waste_confidence: float = Field(..., ge=0.0, le=1.0)
    made_for_kids_official: bool = False
    is_young_kids: bool = False
    granular_sub_category: str | None = None
    thumbnail_url: str | None = None
    detected_language: str | None = None
    detected_country: str | None = None
    topic_categories: list[str] = Field(default_factory=list)
    cost: float
    impressions: int
    views: int
    clicks: int
    conversions: float
    reason_summary: str
    is_masked: bool = False


class WasteCategoryBreakdown(BaseModel):
    """Spend and channel count summary for an individual waste category."""
    category: WasteCategoryType
    wasted_spend: float = 0.0
    wasted_spend_percentage: float = 0.0
    channel_count: int = 0
    impressions: int = 0
    views: int = 0
    clicks: int = 0
    conversions: float = 0.0
    description: str = ""


class CreativeTargetingProfile(BaseModel):
    """Ideal targeting persona and contextual boundaries extracted from an ad creative."""
    ad_url: str | None = None
    ad_title: str | None = None
    brand_or_product: str = "Advertiser Campaign"
    target_persona: str = Field(..., description="Target audience / Ideal Customer Profile (ICP)")
    target_intent: str = Field(default="", description="Core value proposition and intent")
    recommended_contextual_topics: list[str] = Field(
        default_factory=list,
        description="Ideal YouTube topic/category entities (e.g. Cloud computing, Enterprise software)",
    )
    negative_anti_personas: list[str] = Field(
        default_factory=list,
        description="Incompatible audiences/categories (e.g. Children, Toddlers, Gaming, Passive Audio)",
    )
    recommended_languages: list[str] = Field(default_factory=lambda: ["en", "de"])
    profiling_source: str = "gemini"  # 'gemini' | 'heuristic' | 'brief'
    summary: str = ""


class ExpectationVsRealityItem(BaseModel):
    """Individual dimension contrast comparing creative intent against actual delivery."""
    dimension: str
    creative_expectation: str
    delivery_reality: str
    alignment_status: Literal["ON_TARGET", "NEUTRAL", "MISALIGNED", "CRITICAL_WASTE"]


class CreativeAlignmentSummary(BaseModel):
    """Comparison of creative targeting expectations vs actual ad placement delivery."""
    profile: CreativeTargetingProfile
    overall_alignment_score: float = Field(..., ge=0.0, le=10.0, description="1-10 alignment score")
    alignment_verdict: str = Field(..., description="High-level narrative verdict")
    on_target_spend: float = 0.0
    on_target_percentage: float = 0.0
    off_target_spend: float = 0.0
    off_target_percentage: float = 0.0
    neutral_spend: float = 0.0
    neutral_percentage: float = 0.0
    top_misaligned_channels: list[dict[str, Any]] = Field(default_factory=list)
    expectation_vs_reality: list[ExpectationVsRealityItem] = Field(default_factory=list)
    strategic_recommendations: list[str] = Field(default_factory=list)


class AuditSummaryReport(BaseModel):
    """Comprehensive executive audit report generated from placement analysis."""
    total_placements_audited: int
    total_spend: float
    total_wasted_spend: float
    wasted_spend_percentage: float
    total_waste_channels: int
    total_impressions_audited: int = 0
    total_wasted_impressions: int = 0
    wasted_impressions_percentage: float = 0.0
    weighted_quality_score: float = 10.0
    top_topic_categories: list[dict[str, Any]] = Field(default_factory=list)
    currency_code: str = "EUR"
    category_breakdowns: dict[str, WasteCategoryBreakdown]
    top_offenders: list[ClassifiedChannelRecord]
    masked_offenders_count: int = 0
    is_pro_audit: bool = False
    coppa_kids_risk_spend: float = 0.0
    annualized_recoverable_runrate: float = 0.0
    exclusions_csv_path: str | None = None
    shield_65k_csv_path: str | None = None
    html_report_path: str | None = None
    upgrade_prompt: str | None = None
    creative_alignment: CreativeAlignmentSummary | None = None
