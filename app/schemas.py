from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class LinkAnalysisRequest(BaseModel):
    url: HttpUrl


class Competitor(BaseModel):
    name: str
    overview: str = ""
    strengths: list[str] = Field(default_factory=list)
    weaknesses_or_gaps: list[str] = Field(default_factory=list)
    evidence_or_note: str = "AI-generated suggestion; independently verify."


class CompetitorAnalysis(BaseModel):
    brand_overview: str
    brand_name: str
    business_category: str
    main_products_and_services: list[str] = Field(default_factory=list)
    competitors: list[Competitor] = Field(default_factory=list)
    brand_strengths: list[str] = Field(default_factory=list)
    competitive_advantages: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)


class SearchQuery(BaseModel):
    query: str
    platforms: list[str] = Field(default_factory=list)
    intent: str
    business_relevance: str = ""
    target_audience: str = ""


class SEOImprovements(BaseModel):
    primary_keyword: str
    secondary_keywords: list[str] = Field(default_factory=list)
    long_tail_keywords: list[str] = Field(default_factory=list)
    business_keywords: list[str] = Field(default_factory=list)
    recommended_title: str
    title_primary_keyword: str = ""
    title_structure_note: str = ""
    meta_description: str
    supporting_content: list[str] = Field(default_factory=list)


class ServiceItem(BaseModel):
    service_name: str
    description: str
    target_industry: str
    target_customer: str
    main_benefit: str
    source_type: str = "identified_from_website"


class TargetAudience(BaseModel):
    primary_audience: list[str] = Field(default_factory=list)
    secondary_audience: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    business_types: list[str] = Field(default_factory=list)
    customer_profiles: list[str] = Field(default_factory=list)
    location_focus: list[str] = Field(default_factory=list)
    customer_needs: list[str] = Field(default_factory=list)
    customer_interests: list[str] = Field(default_factory=list)
    recommended_marketing_segments: list[str] = Field(default_factory=list)


class AnalysisSections(BaseModel):
    competitor_analysis: CompetitorAnalysis
    target_search_queries: list[SearchQuery] = Field(min_length=5, max_length=5)
    seo_improvements: SEOImprovements
    top_services: list[ServiceItem] = Field(min_length=5, max_length=5)
    target_audience: TargetAudience


class BrandSummary(BaseModel):
    name: str
    category: str
    summary: str


class LinkAnalysisResponse(BaseModel):
    success: bool = True
    website: str
    brand: BrandSummary
    analysis: AnalysisSections
    extracted_content: dict[str, object] | None = None
    model: str
    disclaimer: str = (
        "AI-generated analysis. Competitor suggestions and inferred details "
        "should be independently verified. No search-volume data is provided."
    )


class ErrorResponse(BaseModel):
    detail: str
