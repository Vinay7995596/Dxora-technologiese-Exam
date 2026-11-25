
import json
import logging

from openai import (
    AsyncOpenAI,
    APIError,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from fastapi import HTTPException

from app.config import settings
from app.schemas import AnalysisSections
from app.services.competitor_service import competitor_research_guidance

logger = logging.getLogger(__name__)

client = (
    AsyncOpenAI(api_key=settings.openai_api_key)
    if settings.openai_api_key
    else None
)


def _build_prompt(website: dict) -> str:

    website_json = json.dumps(website, ensure_ascii=False)

    return f"""
You are a professional business, SEO, and marketing analyst.

Analyze ONLY the website evidence provided below.

Do not invent:
- Search volumes
- Rankings
- Revenue
- Customer counts
- Market share

Return one valid JSON object containing these sections:

1. competitor_analysis
2. target_search_queries (exactly 5)
3. seo_improvements
4. top_services (exactly 5)
5. target_audience

For search queries, use these platforms:
Google, Facebook, Instagram, LinkedIn, X (Twitter).

For services, identify actual services wherever possible.
Clearly label inferred recommendations.

{competitor_research_guidance()}

Website evidence:

{website_json}
"""


async def analyze_with_llm(website: dict) -> AnalysisSections:

    if not settings.openai_api_key or client is None:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is not configured. Check your .env file."
        )

    try:

        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return only valid JSON. "
                        "Follow the requested structure exactly."
                    )
                },
                {
                    "role": "user",
                    "content": _build_prompt(website)
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = response.choices[0].message.content

        if not content:
            raise HTTPException(
                status_code=502,
                detail="AI provider returned an empty response."
            )

        parsed = json.loads(content)

        return AnalysisSections.model_validate(parsed)

    except RateLimitError:
        logger.exception("OpenAI rate limit or quota error")
        raise HTTPException(
            status_code=503,
            detail="OpenAI quota or rate limit exceeded. Check API billing."
        )

    except APITimeoutError:
        logger.exception("OpenAI request timed out")
        raise HTTPException(
            status_code=504,
            detail="OpenAI API request timed out."
        )

    except AuthenticationError:
        logger.exception("OpenAI authentication failed")
        raise HTTPException(
            status_code=401,
            detail="Invalid OpenAI API key."
        )

    except APIConnectionError:
        logger.exception("OpenAI connection failed")
        raise HTTPException(
            status_code=502,
            detail="Could not connect to OpenAI API."
        )

    except APIError:
        logger.exception("OpenAI API error")
        raise HTTPException(
            status_code=502,
            detail="OpenAI API request failed. Check terminal logs."
        )

    except json.JSONDecodeError:
        logger.exception("Invalid JSON returned by OpenAI")
        raise HTTPException(
            status_code=502,
            detail="AI provider returned invalid JSON."
        )

    except ValueError:
        logger.exception("AI response validation failed")
        raise HTTPException(
            status_code=502,
            detail="AI response does not match the expected structure."
        )
