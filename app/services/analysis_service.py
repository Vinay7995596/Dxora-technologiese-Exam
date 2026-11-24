from app.config import settings
from app.schemas import BrandSummary, LinkAnalysisResponse
from app.services.llm_service import analyze_with_llm
from app.services.website_extractor import extract_website_content


async def run_link_analysis(url: str) -> LinkAnalysisResponse:
    website = await extract_website_content(url)
    analysis = await analyze_with_llm(website)

    brand = analysis.competitor_analysis
    return LinkAnalysisResponse(
        success=True,
        website=str(website["final_url"]),
        brand=BrandSummary(
            name=brand.brand_name,
            category=brand.business_category,
            summary=brand.brand_overview,
        ),
        analysis=analysis,
        extracted_content={
            "title": website["title"],
            "meta_description": website["meta_description"],
            "headings": website["headings"],
        },
        model=settings.openai_model,
    )
