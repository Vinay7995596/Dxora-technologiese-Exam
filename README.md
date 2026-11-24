# AI-Powered Website Link Analysis API

A FastAPI application that fetches a public website, extracts readable content, and uses an LLM to generate business and marketing insights.

## Features

- `POST /link-analysis` accepts a website URL.
- Fetches public HTML with HTTPX.
- Extracts title, meta description, headings, canonical URL, and visible text with BeautifulSoup.
- Uses an LLM to produce five analysis sections:
  1. Competitor vs. brand details
  2. Five target search queries for Google, Facebook, Instagram, LinkedIn, and X
  3. SEO improvements
  4. Five key services
  5. Target audience identification
- Validates the AI output using Pydantic.
- Handles invalid URLs, inaccessible websites, timeouts, oversized pages, redirects, and AI failures.
- Includes basic SSRF protections against localhost and private/non-public IP destinations.

## Project structure

```text
ai-link-analysis/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── services/
│   │   ├── website_extractor.py
│   │   ├── llm_service.py
│   │   ├── analysis_service.py
│   │   └── competitor_service.py
│   └── utils/
│       └── validators.py
├── tests/
│   └── test_link_analysis.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or newer
- An OpenAI API key with API billing enabled

## Setup on Windows

Open this folder in VS Code and run these commands in the terminal:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy the environment example:

```powershell
copy .env.example .env
```

Open `.env` and replace `your_openai_api_key_here` with your own key. Never commit `.env` to GitHub.

## Run the server

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 4000
```

Open API documentation:

- http://localhost:4000/docs
- Health check: http://localhost:4000/health

## API request

**POST** `http://localhost:4000/link-analysis`

Content-Type: `application/json`

```json
{
  "url": "https://example.com"
}
```

Example cURL:

```bash
curl -X POST "http://localhost:4000/link-analysis" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

The API returns `success`, `website`, `brand`, `analysis`, `extracted_content`, `model`, and a disclaimer. The `analysis` object contains all five assignment sections.

## Run tests

```powershell
pytest -v
```

Tests cover the health endpoint, invalid URL, localhost rejection, and response shape. The success test mocks the analysis service, so it does not spend API credits.

## LLM platform comparison (research snapshot: 24 November 2026)

Prices below are public API list prices in USD per 1 million tokens. Prices can change; re-check provider pricing before submission or deployment.

| Provider / model | Input / 1M | Output / 1M | Context / capability | Notes |
|---|---:|---:|---|---|
| OpenAI GPT-5.4 mini | $0.75 | $4.50 | 400K context; structured outputs supported | Balanced option for more demanding structured analysis |
| Google Gemini 2.5 Flash-Lite | $0.10 | $0.40 | Check current model documentation for context and structured-output limits | Very low-cost option; useful for high-volume extraction and summaries |
| Anthropic Claude Haiku 5.5 | $0.10 (up to 100K prompt) | $0.50 | 1M context; fast model | Low-cost, latency-sensitive extraction and classification |

### Recommendation

For this implementation, GPT-5.4 mini is selected as a practical balance of instruction following, structured output support, and capability for multi-part analysis. This is a reasoned selection, not a claim that it wins every benchmark. No independent latency or accuracy benchmark was run for this assignment.

A cost-first alternative is Gemini 2.5 Flash-Lite. Claude Haiku 5.5 is another low-cost option for extraction and classification. Test the same set of websites against each model before making a production decision.

### Estimated cost per website analysis

Assumption: 20,000 input tokens and 4,000 output tokens for one analysis. This is an estimate, not measured usage.

- GPT-5.4 mini: (20,000 × $0.75 + 4,000 × $4.50) / 1,000,000 = **$0.033**
- Gemini 2.5 Flash-Lite: (20,000 × $0.10 + 4,000 × $0.40) / 1,000,000 = **$0.0036**
- Claude Haiku 5.5: (20,000 × $0.10 + 4,000 × $0.50) / 1,000,000 = **$0.004**

Actual usage depends on website size, prompt length, output length, caching, provider pricing tier, and model tokenization. Provider costs exclude hosting and other infrastructure.

### Cost optimization

1. Remove scripts, styles, navigation, footer, and repeated page content before sending text to the model.
2. Limit extracted text to the most relevant content.
3. Cache analysis by normalized URL and content hash.
4. Avoid repeated LLM calls for the same page content.
5. Use a smaller model for simple classification and extraction.
6. Track actual input/output token usage returned by the provider.
7. Set request timeouts and content-size limits.

## Important limitations and production notes

- Competitors are AI-generated suggestions in this version. A search provider, business directory, or other trusted research source is required to verify competitors and their strengths/weaknesses.
- Search queries are suggestions only. The application does not fetch search-volume, ranking, or social-platform analytics data.
- A single page may not describe every service or audience. The model labels inferred service recommendations.
- This project includes basic SSRF checks, but production deployments should add network-level egress restrictions, DNS pinning/rebinding protection, rate limiting, authentication, logging, and a robust cache.
- Some websites block automated requests, require JavaScript, or return bot-protection pages. Those sites may not be analyzable by this simple HTML-fetching approach.
- Never expose your API key or commit `.env`.

## Official pricing and model references

- OpenAI GPT-5.4 mini: https://developers.openai.com/api/docs/models/gpt-5.4-mini
- OpenAI API pricing: https://developers.openai.com/api/docs/pricing
- Google Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Anthropic Claude Haiku 5.5: https://platform.claude.com/docs/en/models/haiku-5-5/overview
- Anthropic API pricing: https://platform.claude.com/docs/en/about-claude/pricing
