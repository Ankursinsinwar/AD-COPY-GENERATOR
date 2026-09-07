"""
Automated unit tests for History Persistence Service.
"""

from backend.services.history_service import HistoryService


def test_history_save_and_retrieve(temp_dirs):
    """Test saving a campaign to history.json and retrieving it."""
    history_file = temp_dirs["data"] / "history.json"
    history_svc = HistoryService(history_file_path=history_file)

    campaign_payload = {
        "id": "test-id-12345",
        "product_name": "Test History Product",
        "description": "Awesome tool",
        "target_audience": "Founders",
        "platforms": ["google", "facebook"],
        "tone": "casual",
        "variation_count": 2,
        "overall_score": 88.5,
        "results": {"Google Ads": {}}
    }

    saved_rec = history_svc.save_history(campaign_payload)
    assert saved_rec["id"] == "test-id-12345"

    # Retrieve all
    history = history_svc.get_history()
    assert len(history) == 1
    assert history[0]["id"] == "test-id-12345"
    assert history[0]["product_name"] == "Test History Product"

    # Retrieve by ID
    by_id = history_svc.get_history_by_id("test-id-12345")
    assert by_id is not None
    assert by_id["product_name"] == "Test History Product"

    # Retrieve non-existent ID
    none_item = history_svc.get_history_by_id("non-existent-id")
    assert none_item is None
