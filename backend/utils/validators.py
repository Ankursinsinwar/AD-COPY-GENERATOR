"""
Campaign input validation module.

Validates incoming REST request payloads for ad copy generation.
"""

from typing import Dict, Any, Tuple
from backend.config.platforms import PLATFORM_CONFIGS, get_platform_config
from backend.config.tones import TONE_CONFIGS, get_tone_config


def validate_campaign_input(data: Dict[str, Any]) -> Tuple[bool, str, int]:
    """
    Validate campaign payload before trigger generation.
    
    Args:
        data (Dict[str, Any]): Input request payload.
        
    Returns:
        Tuple[bool, str, int]: (is_valid, error_message, status_code)
    """
    if not isinstance(data, dict):
        return False, "Invalid JSON payload", 400

    product_name = str(data.get("product_name", "")).strip()
    if not product_name:
        return False, "Product name is required", 400

    platforms = data.get("platforms", [])
    if isinstance(platforms, str):
        platforms = [p.strip() for p in platforms.split(",") if p.strip()]

    if not isinstance(platforms, list) or len(platforms) == 0:
        return False, "Select at least one platform", 400

    # Validate platform keys
    for p in platforms:
        if not get_platform_config(str(p)):
            return False, f"Invalid platform selected: '{p}'. Supported platforms: {list(PLATFORM_CONFIGS.keys())}", 400

    tone = str(data.get("tone", "professional")).strip().lower()
    if not get_tone_config(tone):
        return False, f"Invalid tone selected: '{tone}'. Supported tones: {list(TONE_CONFIGS.keys())}", 400

    try:
        variation_count = int(data.get("variation_count", 3))
        if variation_count < 1 or variation_count > 3:
            return False, "Variation count must be between 1 and 3", 400
    except (ValueError, TypeError):
        return False, "Variation count must be an integer between 1 and 3", 400

    return True, "", 200
