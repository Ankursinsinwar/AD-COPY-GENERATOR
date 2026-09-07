"""
Centralized Configuration Package for Ad Copy Generator.
"""

from backend.config.platforms import PLATFORM_CONFIGS, get_platform_config
from backend.config.tones import TONE_CONFIGS, get_tone_config

__all__ = ["PLATFORM_CONFIGS", "get_platform_config", "TONE_CONFIGS", "get_tone_config"]
