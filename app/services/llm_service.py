import json
from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError
from fastapi import HTTPException

from app.config import settings
from app.schemas import AnalysisSections
from app.services.competitor_service import competitor_research_guidance

client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


def _build_prompt(website: dict[str, object]) -> str:
    website_json = json.dumps(website, ensure_ascii=False)
    return f"""
You are a careful business, SEO, and marketing analyst.
Analyze ONLY the website evidence below. Do not invent facts, search volumes,
rankings, customer counts, revenue, locations, or market-share data.

Return one valid JSON object matching the requested schema:
- competitor_analysis: brand_overview, brand_name, business_category,
  main_products_and_services, competitors, brand_strengths,
  competitive_advantages, opportunities.
- target_search_queries: exactly 5 objects. Each has query, platforms,
  intent, business_relevance, target_audience. Platforms must be selected
  from Google, Facebook, Instagram, LinkedIn, X (Twitter). These are
  suggested queries, not measured keyword-volume results.
- seo_improvements: primary_keyword, secondary_keywords, long_tail_keywords,
  business_keywords, recommended_title, title_primary_keyword,
  title_structure_note, meta_description, supporting_content.
- top_services: exactly 5 objects with service_name, description,
  target_industry, target_customer, main_benefit, source_type.
  Identify services from website evidence when possible. If fewer than five
  are explicit, fill remaining entries with clearly labelled inferred
  recommendations and set source_type to "inferred_recommendation".
- target_audience: primary_audience, secondary_audience, industries,
  business_types, customer_profiles, location_focus, customer_needs,
  customer_interests, recommended_marketing_segments.

Use concise, specific, useful language. Do not return markdown fences.
{competitor_research_guidance()}

Website evidence:
{website_json}
"""


async def analyze_with_llm(website: dict[str, object]) -> AnalysisSections:
    if not settings.openai_api_key or client is None:
        # raise HTTPException(status_code=503, detail="OpenAI API key is not configured. Add OPENAI_API_KEY to .env.")
         raise HTTPException(
        status_code=503,
        detail="OpenAI API key is not configured. Add OPENAI_API_KEY to .env."
    )

    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "Return only a valid JSON object. Follow the requested structure exactly.",
                },
                {"role": "user", "content": _build_prompt(website)},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=502, detail="The AI model returned an empty response.")

        parsed = json.loads(content)
        return AnalysisSections.model_validate(parsed)

    except (RateLimitError, APITimeoutError):
        raise HTTPException(status_code=503, detail="The AI provider is busy or timed out. Please try again.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="The AI provider returned invalid JSON.")
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"The AI response did not match the expected structure: {exc}")
    except APIError:
        raise HTTPException(status_code=502, detail="The AI provider request failed.")

