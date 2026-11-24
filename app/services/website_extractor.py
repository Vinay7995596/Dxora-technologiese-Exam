import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

from app.config import settings
from app.utils.validators import validate_public_url, validate_redirect


async def _download_html(url: str) -> tuple[str, str]:
    current_url = validate_public_url(url)
    timeout = httpx.Timeout(settings.request_timeout)

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=False,
        trust_env=False,
        headers={"User-Agent": "AILinkAnalysisBot/1.0 (+website content analysis)"},
    ) as client:
        for _ in range(4):
            try:
                async with client.stream("GET", current_url) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise HTTPException(status_code=502, detail="Website returned an invalid redirect.")
                        current_url = validate_redirect(current_url, location)
                        continue

                    if response.status_code >= 400:
                        raise HTTPException(
                            status_code=422,
                            detail=f"Website returned HTTP {response.status_code}.",
                        )

                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                        raise HTTPException(status_code=422, detail="The provided URL does not return an HTML page.")

                    chunks = []
                    total = 0
                    async for chunk in response.aiter_bytes():
                        total += len(chunk)
                        if total > settings.max_html_bytes:
                            raise HTTPException(status_code=413, detail="Website HTML is larger than the allowed limit.")
                        chunks.append(chunk)
                    encoding = response.encoding or "utf-8"
                    return b"".join(chunks).decode(encoding, errors="replace"), str(response.url)

            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Timed out while fetching the website.")
            except httpx.RequestError:
                raise HTTPException(status_code=502, detail="Could not connect to the provided website.")

    raise HTTPException(status_code=502, detail="Too many website redirects.")


async def extract_website_content(url: str) -> dict[str, object]:
    html, final_url = await _download_html(url)
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "noscript", "svg", "iframe", "nav", "footer"]):
        element.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "").strip() if description_tag else ""

    headings = {
        "h1": [tag.get_text(" ", strip=True) for tag in soup.find_all("h1")[:8]],
        "h2": [tag.get_text(" ", strip=True) for tag in soup.find_all("h2")[:15]],
        "h3": [tag.get_text(" ", strip=True) for tag in soup.find_all("h3")[:15]],
    }
    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href", "") if canonical_tag else ""

    main = soup.find("main") or soup.body or soup
    text = " ".join(main.stripped_strings)
    text = " ".join(text.split())[: settings.max_text_chars]

    if len(text) < 80:
        raise HTTPException(
            status_code=422,
            detail="Not enough readable text was found on this website to analyze it.",
        )

    return {
        "requested_url": url,
        "final_url": final_url,
        "title": title,
        "meta_description": description,
        "canonical_url": canonical,
        "headings": headings,
        "text": text,
    }
