"""
Automated unit tests for REST API endpoints.
"""

from unittest.mock import patch


def test_flask_init_and_health_check(client):
    """Test Flask application initialization and /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "groq_configured" in data
    assert "model" in data


def test_api_generate_success(client, mock_groq_service):
    """Test successful POST /api/generate endpoint with mocked Groq service."""
    with patch("backend.routes.api.ad_generator_service.groq_service", mock_groq_service):
        payload = {
            "product_name": "CloudSync Pro",
            "description": "Automatic secure cloud backup software",
            "target_audience": "IT Managers",
            "platforms": ["google", "facebook"],
            "tone": "professional",
            "variation_count": 3
        }
        response = client.post("/api/generate", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "campaign" in data
        campaign = data["campaign"]
        assert campaign["product_name"] == "CloudSync Pro"
        assert len(campaign["results"]) == 2


def test_api_generate_validation_empty_product(client):
    """Test /api/generate returns HTTP 400 when product_name is empty."""
    payload = {
        "product_name": "",
        "platforms": ["google"]
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Product name is required" in data["error"]


def test_api_generate_validation_no_platform(client):
    """Test /api/generate returns HTTP 400 when platforms list is empty."""
    payload = {
        "product_name": "SaaS Platform",
        "platforms": []
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Select at least one platform" in data["error"]


def test_api_generate_validation_invalid_platform(client):
    """Test /api/generate returns HTTP 400 for unsupported platform key."""
    payload = {
        "product_name": "SaaS Platform",
        "platforms": ["invalid_platform_key"]
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Invalid platform selected" in data["error"]


def test_api_generate_validation_invalid_tone(client):
    """Test /api/generate returns HTTP 400 for unsupported tone key."""
    payload = {
        "product_name": "SaaS Platform",
        "platforms": ["google"],
        "tone": "super_funny_invalid"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Invalid tone selected" in data["error"]


def test_api_history_endpoints(client, mock_groq_service):
    """Test GET /api/history and GET /api/history/<id> endpoints."""
    # First generate a campaign
    with patch("backend.routes.api.ad_generator_service.groq_service", mock_groq_service):
        payload = {
            "product_name": "Test History App",
            "platforms": ["google"],
            "tone": "casual"
        }
        gen_res = client.post("/api/generate", json=payload)
        assert gen_res.status_code == 200
        campaign_id = gen_res.get_json()["campaign"]["id"]

    # Fetch history list
    hist_res = client.get("/api/history")
    assert hist_res.status_code == 200
    hist_data = hist_res.get_json()
    assert hist_data["status"] == "success"
    assert isinstance(hist_data["history"], list)
    assert len(hist_data["history"]) > 0

    # Fetch specific campaign by ID
    item_res = client.get(f"/api/history/{campaign_id}")
    assert item_res.status_code == 200
    item_data = item_res.get_json()
    assert item_data["status"] == "success"
    assert item_data["campaign"]["id"] == campaign_id
