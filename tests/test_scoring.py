"""
Automated unit tests for Copy Scoring Service.
"""

from backend.services.scoring_service import CopyScoringService


def test_scoring_calculation_formula():
    """Verify quality score metric evaluation and overall score formula."""
    headline = "Transform Your Business Overnight"
    body = "Our AI platform helps teams double conversion rates effortlessly."
    cta = "Get Started Now"
    hashtags = ["#ai", "#growth"]

    scores = CopyScoringService.evaluate_copy(
        headline=headline,
        body=body,
        cta=cta,
        hashtags=hashtags,
        platform_key="instagram"
    )

    assert "headline_strength" in scores
    assert "clarity" in scores
    assert "emotional_appeal" in scores
    assert "cta_effectiveness" in scores
    assert "overall" in scores
    assert "strengths" in scores
    assert "suggestions" in scores

    # Verify 30/25/25/20 weighted formula match
    expected_overall = round(
        (scores["headline_strength"] * 0.30) +
        (scores["clarity"] * 0.25) +
        (scores["emotional_appeal"] * 0.25) +
        (scores["cta_effectiveness"] * 0.20),
        1
    )
    assert scores["overall"] == expected_overall


def test_scoring_differentiated_scores():
    """Verify scores are realistic and differentiated (not all identical or uniform 90+)."""
    # Strong copy
    strong_eval = CopyScoringService.evaluate_copy(
        headline="Unlock Exclusive Access Today",
        body="Get instant access to top tier resources.",
        cta="Claim Discount",
        hashtags=["#exclusive"],
        platform_key="facebook"
    )

    # Weak copy
    weak_eval = CopyScoringService.evaluate_copy(
        headline="",
        body="a",
        cta="",
        hashtags=[],
        platform_key="google"
    )

    assert strong_eval["overall"] > weak_eval["overall"]
    assert weak_eval["overall"] < 60.0
