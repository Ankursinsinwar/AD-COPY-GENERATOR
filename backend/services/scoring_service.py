"""
Deterministic Copy Scoring & Analytics Engine.

Evaluates ad copy variations across 5 key marketing metrics:
- Headline Strength (30%)
- Clarity (25%)
- Emotional Appeal (25%)
- CTA Effectiveness (20%)

Generates explainable overall scores, key strengths, and improvement suggestions.
"""

from typing import Dict, Any, List


class CopyScoringService:
    """Service for evaluating and scoring generated ad copy variants."""

    @staticmethod
    def evaluate_copy(
        headline: str,
        body: str,
        cta: str,
        hashtags: List[str],
        platform_key: str,
        ai_scores: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compute quality scores, strengths, and improvement suggestions for an ad copy.
        
        Args:
            headline (str): Headline text.
            body (str): Body or primary text.
            cta (str): Call to Action text.
            hashtags (List[str]): List of hashtags.
            platform_key (str): Target platform identifier.
            ai_scores (Optional[Dict[str, Any]]): AI-suggested scores to refine.
            
        Returns:
            Dict[str, Any]: Structured scores dictionary with overall, metrics, strengths, suggestions.
        """
        headline_str = str(headline or "").strip()
        body_str = str(body or "").strip()
        cta_str = str(cta or "").strip()

        # If AI provided scores, validate and use as base with fallback bounded heuristics
        base_headline = CopyScoringService._extract_score(ai_scores, "headline_strength", 72)
        base_clarity = CopyScoringService._extract_score(ai_scores, "clarity", 80)
        base_emotional = CopyScoringService._extract_score(ai_scores, "emotional_appeal", 75)
        base_cta = CopyScoringService._extract_score(ai_scores, "cta_effectiveness", 78)

        # Deterministic adjustments based on copy heuristics
        headline_len = len(headline_str)
        if headline_len == 0:
            headline_score = 40.0
        elif 15 <= headline_len <= 50:
            headline_score = min(98.0, base_headline + 5.0)
        else:
            headline_score = max(55.0, base_headline - 5.0)

        # Clarity based on body structure and conciseness
        body_words = len(body_str.split())
        if 10 <= body_words <= 40:
            clarity_score = min(98.0, base_clarity + 4.0)
        elif body_words > 60:
            clarity_score = max(60.0, base_clarity - 8.0)
        else:
            clarity_score = base_clarity

        # Emotional appeal heuristic (power words / punctuation)
        power_words = {"free", "exclusive", "proven", "instant", "transform", "secret", "guaranteed", "master", "boost", "effortless", "save", "limited", "unlock"}
        found_power = any(w in body_str.lower() or w in headline_str.lower() for w in power_words)
        emotional_score = min(96.0, base_emotional + (8.0 if found_power else -3.0))

        # CTA score
        action_verbs = {"get", "start", "claim", "download", "join", "buy", "learn", "try", "discover", "book", "save"}
        has_action = any(v in cta_str.lower() for v in action_verbs) if cta_str else False
        cta_score = 90.0 if has_action else (65.0 if cta_str else 40.0)

        # Compute overall score: 30% headline, 25% clarity, 25% emotional appeal, 20% CTA
        overall_score = round(
            (headline_score * 0.30) +
            (clarity_score * 0.25) +
            (emotional_score * 0.25) +
            (cta_score * 0.20),
            1
        )

        # Generate explainable strengths and suggestions
        strengths = CopyScoringService._generate_strengths(headline_score, clarity_score, emotional_score, cta_score, found_power, has_action)
        suggestions = CopyScoringService._generate_suggestions(headline_score, clarity_score, emotional_score, cta_score, headline_len, platform_key)

        return {
            "headline_strength": round(headline_score, 1),
            "clarity": round(clarity_score, 1),
            "emotional_appeal": round(emotional_score, 1),
            "cta_effectiveness": round(cta_score, 1),
            "overall": overall_score,
            "strengths": strengths,
            "suggestions": suggestions
        }

    @staticmethod
    def _extract_score(ai_scores: Optional[Dict[str, Any]], key: str, default_val: float) -> float:
        if not ai_scores or not isinstance(ai_scores, dict):
            return default_val
        val = ai_scores.get(key)
        try:
            num = float(val)
            return max(30.0, min(99.0, num))
        except (ValueError, TypeError):
            return default_val

    @staticmethod
    def _generate_strengths(headline_s: float, clarity_s: float, emotional_s: float, cta_s: float, power_words: bool, has_action: bool) -> List[str]:
        strengths = []
        if headline_s >= 80:
            strengths.append("High-impact headline tailored for hook retention.")
        if clarity_s >= 80:
            strengths.append("Concise body messaging with excellent readability.")
        if emotional_s >= 80 or power_words:
            strengths.append("Strong emotional resonance using persuasive power triggers.")
        if cta_s >= 80 or has_action:
            strengths.append("Clear, action-oriented Call to Action driving conversions.")
        if not strengths:
            strengths.append("Solid overall compliance with platform formatting requirements.")
        return strengths

    @staticmethod
    def _generate_suggestions(headline_s: float, clarity_s: float, emotional_s: float, cta_s: float, headline_len: int, platform: str) -> List[str]:
        suggestions = []
        if headline_s < 80:
            suggestions.append(f"Consider shortening or sharpening the headline to maximize {platform} engagement.")
        if emotional_s < 80:
            suggestions.append("Add sensory or FOMO trigger words to heighten emotional response.")
        if cta_s < 80:
            suggestions.append("Upgrade the CTA with an explicit action verb like 'Claim', 'Unlock', or 'Get Started'.")
        if clarity_s < 80:
            suggestions.append("Break up long sentences into punchier value propositions.")
        if not suggestions:
            suggestions.append("Test this variant against smaller target demographic segments.")
        return suggestions
