from fastapi.testclient import TestClient
from app.main import app
from app.services import analysis_service

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_url_is_rejected():
    response = client.post("/link-analysis", json={"url": "not-a-url"})
    assert response.status_code == 422


def test_private_network_url_is_rejected(monkeypatch):
    # The URL validation function performs DNS checks. localhost is rejected
    # before any network request is made.
    response = client.post("/link-analysis", json={"url": "http://localhost"})
    assert response.status_code == 400


def test_success_response_shape(monkeypatch):
    from app.schemas import (
        AnalysisSections, CompetitorAnalysis, SearchQuery, SEOImprovements,
        ServiceItem, TargetAudience, Competitor
    )

    fake_analysis = AnalysisSections(
        competitor_analysis=CompetitorAnalysis(
            brand_overview="A sample company.",
            brand_name="Sample",
            business_category="Technology",
            main_products_and_services=["Web development"],
            competitors=[
                Competitor(name=f"Competitor {i}", overview="Suggested competitor.")
                for i in range(1, 4)
            ],
            brand_strengths=["Clear service offering"],
            competitive_advantages=["Focused solution"],
            opportunities=["Publish case studies"],
        ),
        target_search_queries=[
            SearchQuery(query=f"sample query {i}", platforms=["Google"],
                        intent="Service discovery")
            for i in range(1, 6)
        ],
        seo_improvements=SEOImprovements(
            primary_keyword="web development",
            recommended_title="Sample Web Development Services",
            meta_description="Sample company web development services.",
        ),
        top_services=[
            ServiceItem(
                service_name=f"Service {i}", description="Description",
                target_industry="Technology", target_customer="Businesses",
                main_benefit="Saves time"
            )
            for i in range(1, 6)
        ],
        target_audience=TargetAudience(primary_audience=["Small businesses"]),
    )

    async def fake_run(url):
        from app.schemas import BrandSummary, LinkAnalysisResponse
        return LinkAnalysisResponse(
            success=True, website=url,
            brand=BrandSummary(name="Sample", category="Technology", summary="A sample company."),
            analysis=fake_analysis, model="test-model"
        )

    import app.main as main_module
    monkeypatch.setattr(main_module, "run_link_analysis", fake_run)
    response = client.post("/link-analysis", json={"url": "https://example.com"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert len(body["analysis"]["target_search_queries"]) == 5
    assert len(body["analysis"]["top_services"]) == 5
