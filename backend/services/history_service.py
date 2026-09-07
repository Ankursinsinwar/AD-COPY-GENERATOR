"""
History Persistence Service.

Manages saving and retrieving campaign generation history stored locally in data/history.json.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Base directory for history persistence
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "history.json"


class HistoryService:
    """Service managing local file persistence for campaign generation history."""

    def __init__(self, history_file_path: Optional[Path] = None):
        """
        Initialize history service and ensure storage directory exists.
        
        Args:
            history_file_path (Optional[Path]): Override history file location if provided.
        """
        self.file_path = history_file_path or HISTORY_FILE
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Create data directory and history.json file if they do not exist."""
        try:
            os.makedirs(self.file_path.parent, exist_ok=True)
            if not self.file_path.exists():
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
        except Exception as e:
            logger.error(f"Failed to initialize history storage file: {e}")

    def save_history(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a newly generated campaign to history.
        
        Args:
            campaign_data (Dict[str, Any]): Generated campaign payload.
            
        Returns:
            Dict[str, Any]: Persisted campaign item with campaign_id and timestamp.
        """
        self._ensure_storage_exists()
        
        campaign_id = campaign_data.get("id") or campaign_data.get("campaign_id") or str(uuid.uuid4())
        timestamp = campaign_data.get("created_at") or campaign_data.get("timestamp") or datetime.now().isoformat()

        record = {
            "id": campaign_id,
            "campaign_id": campaign_id,
            "timestamp": timestamp,
            "product": campaign_data.get("product", campaign_data.get("product_name", "")),
            "product_name": campaign_data.get("product_name", campaign_data.get("product", "")),
            "description": campaign_data.get("description", ""),
            "audience": campaign_data.get("audience", campaign_data.get("target_audience", "")),
            "target_audience": campaign_data.get("target_audience", campaign_data.get("audience", "")),
            "selected_platforms": campaign_data.get("selected_platforms", campaign_data.get("platforms", [])),
            "platforms": campaign_data.get("platforms", campaign_data.get("selected_platforms", [])),
            "tone": campaign_data.get("tone", "professional"),
            "variation_count": campaign_data.get("variation_count", 3),
            "overall_score": campaign_data.get("overall_score", 0.0),
            "results": campaign_data.get("results", {})
        }

        try:
            history = self._read_raw_history()
            # Insert at beginning for reverse chronological order
            history.insert(0, record)
            # Keep up to 100 entries in file
            history = history[:100]
            
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)

            return record
        except Exception as e:
            logger.error(f"Failed to save campaign to history file: {e}")
            return record

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve latest campaigns in reverse chronological order.
        
        Args:
            limit (int): Maximum number of entries to return (default 20).
            
        Returns:
            List[Dict[str, Any]]: List of campaign records.
        """
        self._ensure_storage_exists()
        history = self._read_raw_history()
        return history[:limit]

    def get_history_by_id(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific campaign by ID.
        
        Args:
            campaign_id (str): Unique campaign identifier.
            
        Returns:
            Optional[Dict[str, Any]]: Campaign record if found, None otherwise.
        """
        self._ensure_storage_exists()
        history = self._read_raw_history()
        for item in history:
            if item.get("id") == campaign_id or item.get("campaign_id") == campaign_id:
                return item
        return None

    def _read_raw_history(self) -> List[Dict[str, Any]]:
        """Safely read raw list from history.json."""
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Failed to read history JSON file: {e}")
            return []
