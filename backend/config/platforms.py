"""
Centralized Platform Configurations and Generation Rules.

Defines specs, character limits, formatting rules, and hashtag requirements
for all supported advertising platforms.
"""

from typing import Dict, Any, Optional

PLATFORM_CONFIGS: Dict[str, Dict[str, Any]] = {
    "google": {
        "key": "google",
        "name": "Google Ads",
        "format": "Search Ad",
        "icon": "fa-google",
        "character_limits": {
            "headline": 30,
            "description": 90,
            "max_headlines": 3,
            "max_descriptions": 2,
        },
        "hashtags_required": False,
        "rules": [
            "Search Ad format",
            "Maximum 3 headlines (up to 30 characters each)",
            "Maximum 2 descriptions (up to 90 characters each)",
            "Use sentence case",
            "Avoid exclamation marks in headlines",
            "No hashtags"
        ]
    },
    "facebook": {
        "key": "facebook",
        "name": "Facebook",
        "format": "Feed Ad",
        "icon": "fa-facebook",
        "character_limits": {
            "primary_text": 125,
            "headline": 40,
        },
        "hashtags_required": False,
        "rules": [
            "Feed Ad format",
            "Primary text up to 125 characters to avoid truncation",
            "Headline up to 40 characters",
            "Start primary text with a strong hook",
            "Conversational and engaging copy"
        ]
    },
    "instagram": {
        "key": "instagram",
        "name": "Instagram",
        "format": "Feed / Story Ad",
        "icon": "fa-instagram",
        "character_limits": {
            "caption": 125,
        },
        "hashtags_required": True,
        "rules": [
            "Feed / Story Ad format",
            "Initial capture text approximately 125 characters",
            "Focus on visual lifestyle and emotional triggers",
            "Include 3-5 relevant hashtags at the end"
        ]
    },
    "linkedin": {
        "key": "linkedin",
        "name": "LinkedIn",
        "format": "Sponsored Content",
        "icon": "fa-linkedin",
        "character_limits": {
            "intro": 150,
            "headline": 70,
        },
        "hashtags_required": True,
        "rules": [
            "Sponsored Content format",
            "Introductory text up to 150 characters",
            "Headline up to 70 characters",
            "Professional and authoritative tone targeting B2B decision makers",
            "Lead with industry insights or statistics",
            "Include 2-3 relevant B2B hashtags"
        ]
    },
    "twitter": {
        "key": "twitter",
        "name": "Twitter/X",
        "format": "Promoted Tweet",
        "icon": "fa-twitter",
        "character_limits": {
            "total": 280,
        },
        "hashtags_required": True,
        "rules": [
            "Promoted Tweet format",
            "Maximum 280 characters total (including body, CTA, and hashtags)",
            "Concise, snappy, and impactful copy",
            "Conversational tone",
            "Include 1-2 trending/relevant hashtags"
        ]
    }
}

# Alias map for flexible key lookup
PLATFORM_ALIASES: Dict[str, str] = {
    "google": "google",
    "google ads": "google",
    "google_ads": "google",
    "facebook": "facebook",
    "fb": "facebook",
    "instagram": "instagram",
    "ig": "instagram",
    "linkedin": "linkedin",
    "twitter": "twitter",
    "twitter/x": "twitter",
    "twitter_x": "twitter",
    "x": "twitter"
}


def get_platform_config(platform_key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve platform configuration by platform key or name.
    
    Args:
        platform_key (str): Key or display name of the platform (case-insensitive).
        
    Returns:
        Optional[Dict[str, Any]]: Configuration dictionary or None if unsupported.
    """
    normalized = str(platform_key).strip().lower()
    canonical_key = PLATFORM_ALIASES.get(normalized, normalized)
    return PLATFORM_CONFIGS.get(canonical_key)
