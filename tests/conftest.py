"""
Pytest configuration and test client fixtures for Ad Copy Generator.
"""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Ensure project root is in python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app


@pytest.fixture
def temp_dirs(monkeypatch):
    """Fixture providing temporary directories for history and exports during tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        exports_dir = tmp_path / "exports"
        data_dir = tmp_path / "data"
        exports_dir.mkdir()
        data_dir.mkdir()

        monkeypatch.setenv("EXPORTS_DIR", str(exports_dir))
        monkeypatch.setenv("DATA_DIR", str(data_dir))
        yield {"exports": exports_dir, "data": data_dir}


@pytest.fixture
def app(temp_dirs):
    """Create Flask application configured for testing environment."""
    app = create_app("testing")
    app.config["EXPORTS_DIR"] = temp_dirs["exports"]
    app.config["DATA_DIR"] = temp_dirs["data"]
    yield app


@pytest.fixture
def client(app):
    """A test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def mock_groq_service(monkeypatch):
    """Mock Groq service fixture to prevent actual network/API calls."""
    mock_service = MagicMock()
    mock_service.is_configured.return_value = True
    
    sample_json = """{
      "platform": "Instagram",
      "variations": [
        {
          "id": "A",
          "label": "Feature-Focused",
          "headline": "Transform Your Marketing",
          "body": "Boost conversions with AI ad copies.",
          "cta": "Get Started",
          "hashtags": ["#marketing", "#ai"]
        },
        {
          "id": "B",
          "label": "Benefit-Focused",
          "headline": "Save 10+ Hours Every Week",
          "body": "Automate copy creation instantly.",
          "cta": "Claim Trial",
          "hashtags": ["#productivity"]
        },
        {
          "id": "C",
          "label": "Urgency-Focused",
          "headline": "Limited Seats Available",
          "body": "Claim your discount today before time runs out.",
          "cta": "Join Now",
          "hashtags": ["#urgent"]
        }
      ]
    }"""
    
    mock_service.generate_completion.return_value = (True, sample_json, {"error": "", "is_quota_exceeded": False})
    return mock_service
