"""
Automated unit tests for centralized platform and tone configurations.
"""

from backend.config.platforms import PLATFORM_CONFIGS, get_platform_config
from backend.config.tones import TONE_CONFIGS, get_tone_config


def test_all_five_platforms_exist():
    """Verify all 5 required platforms exist in centralized configuration."""
    required_keys = ["google", "facebook", "instagram", "linkedin", "twitter"]
    for key in required_keys:
        assert key in PLATFORM_CONFIGS
        cfg = get_platform_config(key)
        assert cfg is not None
        assert "name" in cfg
        assert "character_limits" in cfg
        assert "rules" in cfg


def test_google_ads_config_rules():
    """Verify Google Ads search ad rules and limits."""
    google = get_platform_config("google")
    limits = google["character_limits"]
    assert limits["headline"] == 30
    assert limits["description"] == 90
    assert limits["max_headlines"] == 3
    assert limits["max_descriptions"] == 2
    assert google["hashtags_required"] is False


def test_facebook_config_rules():
    """Verify Facebook feed ad rules and limits."""
    fb = get_platform_config("facebook")
    limits = fb["character_limits"]
    assert limits["primary_text"] == 125
    assert limits["headline"] == 40


def test_instagram_config_rules():
    """Verify Instagram rules and hashtag requirement."""
    ig = get_platform_config("instagram")
    limits = ig["character_limits"]
    assert limits["caption"] == 125
    assert ig["hashtags_required"] is True


def test_linkedin_config_rules():
    """Verify LinkedIn rules and limits."""
    li = get_platform_config("linkedin")
    limits = li["character_limits"]
    assert limits["intro"] == 150
    assert limits["headline"] == 70


def test_twitter_config_rules():
    """Verify Twitter/X 280-character total limit."""
    tw = get_platform_config("twitter")
    limits = tw["character_limits"]
    assert limits["total"] == 280


def test_six_tones_exist():
    """Verify all 6 required tones exist with descriptions."""
    required_tones = ["professional", "casual", "urgent", "humorous", "emotional", "minimalist"]
    for t_key in required_tones:
        assert t_key in TONE_CONFIGS
        t_cfg = get_tone_config(t_key)
        assert t_cfg is not None
        assert "description" in t_cfg
        assert len(t_cfg["description"]) > 10
