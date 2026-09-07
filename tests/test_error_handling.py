"""
Automated unit tests for error handling and edge cases.
"""

from unittest.mock import patch, MagicMock
from backend.services.ad_generator import AdGeneratorService


def test_groq_quota_exceeded_handling(mock_groq_service):
    """Test platform-level error handling when Groq API returns HTTP 429 quota error."""
    mock_groq_service.generate_completion.return_value = (
        False, "", {"error": "Quota exceeded", "is_quota_exceeded": True, "error_type": "QUOTA_EXCEEDED"}
    )

    generator = AdGeneratorService(groq_service=mock_groq_service)
    res = generator.generate_campaign(
        product_name="Rate Limit App",
        description="Testing 429 error",
        target_audience="Devs",
        platforms=["google"],
        tone="professional"
    )

    assert "Google Ads" in res["results"]
    card = res["results"]["Google Ads"]
    assert "error" in card
    assert card["is_quota_exceeded"] is True
    assert "Quota exceeded" in card["error"]


def test_api_404_error_handler(client):
    """Test custom 404 handler for API routes."""
    res = client.get("/api/non-existent-endpoint")
    assert res.status_code == 404
    data = res.get_json()
    assert "Resource or endpoint not found" in data["error"]


def test_api_export_empty_payload(client):
    """Test POST /api/export/csv with empty payload returns HTTP 400."""
    res = client.post("/api/export/csv", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert "No campaign data provided" in data["error"]
