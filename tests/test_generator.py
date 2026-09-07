"""
Automated unit tests for Ad Generator Service.
"""

from unittest.mock import patch, MagicMock
from backend.services.ad_generator import AdGeneratorService


def test_generator_single_and_multi_platform(mock_groq_service):
    """Test single and multi-platform generation flow."""
    generator = AdGeneratorService(groq_service=mock_groq_service)

    # Test single platform
    single_res = generator.generate_campaign(
        product_name="Product Alpha",
        description="Great product",
        target_audience="General",
        platforms=["google"],
        tone="professional",
        variation_count=2
    )
    assert single_res["product_name"] == "Product Alpha"
    assert "Google Ads" in single_res["results"]
    assert len(single_res["results"]["Google Ads"]["variations"]) == 2

    # Test all 5 platforms
    all_platforms = ["google", "facebook", "instagram", "linkedin", "twitter"]
    multi_res = generator.generate_campaign(
        product_name="Product Multi",
        description="Multi platform test",
        target_audience="All Marketers",
        platforms=all_platforms,
        tone="urgent",
        variation_count=3
    )
    assert len(multi_res["results"]) == 5
    for p_name in ["Google Ads", "Facebook", "Instagram", "LinkedIn", "Twitter/X"]:
        assert p_name in multi_res["results"]
        assert len(multi_res["results"][p_name]["variations"]) == 3


def test_generator_variation_counts(mock_groq_service):
    """Test generating 1, 2, and 3 variation counts."""
    generator = AdGeneratorService(groq_service=mock_groq_service)

    for count in [1, 2, 3]:
        res = generator.generate_campaign(
            product_name="Variant Test",
            description="Testing counts",
            target_audience="Devs",
            platforms=["facebook"],
            tone="casual",
            variation_count=count
        )
        vars_list = res["results"]["Facebook"]["variations"]
        assert len(vars_list) == count
        if count >= 1: assert vars_list[0]["id"] == "A"
        if count >= 2: assert vars_list[1]["id"] == "B"
        if count >= 3: assert vars_list[2]["id"] == "C"
