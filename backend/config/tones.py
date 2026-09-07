"""
Centralized Tone Configurations & Style Controllers.

Defines tone descriptions for prompt construction and validation.
"""

from typing import Dict, Any, Optional

TONE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "professional": {
        "key": "professional",
        "name": "Professional",
        "description": "Authoritative, polished, business-focused, and credibility-building."
    },
    "casual": {
        "key": "casual",
        "name": "Casual",
        "description": "Friendly, conversational, warm, and approachable."
    },
    "urgent": {
        "key": "urgent",
        "name": "Urgent",
        "description": "Time-sensitive, action-driven, with FOMO and scarcity elements."
    },
    "humorous": {
        "key": "humorous",
        "name": "Humorous",
        "description": "Witty, playful, clever, memorable, with light humor and wordplay."
    },
    "emotional": {
        "key": "emotional",
        "name": "Emotional",
        "description": "Empathetic, inspiring, feeling-focused, and story-driven."
    },
    "minimalist": {
        "key": "minimalist",
        "name": "Minimalist",
        "description": "Ultra-clean, direct, stripped of fluff, with maximum impact in the fewest words."
    }
}


def get_tone_config(tone_key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve tone configuration by key.
    
    Args:
        tone_key (str): Tone key (case-insensitive).
        
    Returns:
        Optional[Dict[str, Any]]: Tone configuration dictionary or None if invalid.
    """
    normalized = str(tone_key).strip().lower()
    return TONE_CONFIGS.get(normalized)
