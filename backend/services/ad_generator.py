"""
AI Ad Copy Generator Orchestrator Service.

Constructs prompts incorporating platform constraints, tone specifications, and A/B variation directives.
Executes completions via Groq Service, parses JSON using multi-method fallbacks, scores output using CopyScoringService,
and persists results to HistoryService.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from backend.config.platforms import get_platform_config, PLATFORM_CONFIGS
from backend.config.tones import get_tone_config, TONE_CONFIGS
from backend.utils.constants import SYSTEM_PROMPT, VARIATION_ANGLES
from backend.utils.json_parser import extract_json
from backend.services.groq_service import GroqService
from backend.services.scoring_service import CopyScoringService
from backend.services.history_service import HistoryService

logger = logging.getLogger(__name__)


class AdGeneratorService:
    """Core business logic service orchestrating AI copy generation."""

    def __init__(
        self,
        groq_service: Optional[GroqService] = None,
        history_service: Optional[HistoryService] = None
    ):
        self.groq_service = groq_service or GroqService()
        self.history_service = history_service or HistoryService()

    def generate_campaign(
        self,
        product_name: str,
        description: str,
        target_audience: str,
        platforms: List[str],
        tone: str = "professional",
        variation_count: int = 3
    ) -> Dict[str, Any]:
        """
        Generate platform-specific ad copies and A/B variations across selected platforms.
        
        Args:
            product_name (str): Product or service name.
            description (str): Key features and benefits.
            target_audience (str): Target demographic description.
            platforms (List[str]): List of target platform keys or names.
            tone (str): Selected tone key.
            variation_count (int): Number of variations per platform (1-3).
            
        Returns:
            Dict[str, Any]: Campaign generation payload containing metadata and results per platform.
        """
        campaign_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        tone_cfg = get_tone_config(tone) or TONE_CONFIGS.get("professional", {})
        tone_name = tone_cfg.get("name", tone.capitalize())
        tone_desc = tone_cfg.get("description", "")

        results = {}
        all_scores = []
        is_partial_error = False

        for platform_key in platforms:
            p_config = get_platform_config(platform_key)
            if not p_config:
                continue

            platform_display_name = p_config["name"]
            
            # Generate variations for this platform
            platform_result, platform_scores = self._generate_for_platform(
                product_name=product_name,
                description=description,
                target_audience=target_audience,
                p_config=p_config,
                tone_name=tone_name,
                tone_desc=tone_desc,
                variation_count=variation_count
            )

            results[platform_display_name] = platform_result
            if platform_scores:
                all_scores.extend(platform_scores)
            if "error" in platform_result:
                is_partial_error = True

        overall_campaign_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

        campaign_data = {
            "id": campaign_id,
            "campaign_id": campaign_id,
            "created_at": created_at,
            "product_name": product_name,
            "description": description,
            "target_audience": target_audience,
            "platforms": platforms,
            "selected_platforms": platforms,
            "tone": tone,
            "variation_count": variation_count,
            "overall_score": overall_campaign_score,
            "results": results,
            "is_partial_error": is_partial_error
        }

        # Save to local history persistence
        try:
            self.history_service.save_history(campaign_data)
        except Exception as e:
            logger.error(f"Failed to persist campaign in history: {e}")

        return campaign_data

    def _generate_for_platform(
        self,
        product_name: str,
        description: str,
        target_audience: str,
        p_config: Dict[str, Any],
        tone_name: str,
        tone_desc: str,
        variation_count: int
    ) -> tuple[Dict[str, Any], List[float]]:
        """Generate ad variations for a specific platform."""
        platform_key = p_config["key"]
        platform_name = p_config["name"]

        # Select A/B variation angles based on variation_count
        angle_keys = ["A", "B", "C"][:variation_count]
        angles = [VARIATION_ANGLES[k] for k in angle_keys]

        # Build detailed user prompt
        user_prompt = self._build_prompt(
            product_name=product_name,
            description=description,
            target_audience=target_audience,
            p_config=p_config,
            tone_name=tone_name,
            tone_desc=tone_desc,
            angles=angles
        )

        success, raw_text, meta = self.groq_service.generate_completion(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.7
        )

        if not success:
            error_card = {
                "platform": platform_name,
                "error": meta.get("error", "Failed to generate copy from Groq API."),
                "is_quota_exceeded": meta.get("is_quota_exceeded", False),
                "variations": []
            }
            return error_card, []

        # Parse JSON output via extract_json
        parsed_ok, parsed_data, parse_err = extract_json(raw_text)
        if not parsed_ok or not isinstance(parsed_data, dict):
            # Fallback parsing attempt if output was a list directly
            if parsed_ok and isinstance(parsed_data, list):
                parsed_data = {"variations": parsed_data}
            else:
                # Local fallback variant construction to prevent app crash
                return self._build_fallback_platform_result(
                    platform_name, p_config, angles, product_name, parse_err
                )

        raw_variations = parsed_data.get("variations", [])
        if not isinstance(raw_variations, list):
            raw_variations = []

        processed_variations = []
        platform_scores = []

        for idx, angle in enumerate(angles):
            var_id = angle["id"]
            var_label = angle["label"]

            # Match raw variation by id or index
            matched_raw = None
            for rv in raw_variations:
                if isinstance(rv, dict) and str(rv.get("id", "")).upper() == var_id:
                    matched_raw = rv
                    break
            if not matched_raw and idx < len(raw_variations) and isinstance(raw_variations[idx], dict):
                matched_raw = raw_variations[idx]
            if not matched_raw:
                matched_raw = {}

            headline = str(matched_raw.get("headline", f"{product_name} — {var_label}")).strip()
            body = str(matched_raw.get("body", matched_raw.get("description", description or product_name))).strip()
            cta = str(matched_raw.get("cta", "Learn More")).strip()
            
            hashtags = matched_raw.get("hashtags", [])
            if isinstance(hashtags, str):
                hashtags = [h.strip() for h in hashtags.split() if h.strip()]
            if not isinstance(hashtags, list):
                hashtags = []

            # Evaluate scores via CopyScoringService
            ai_score_obj = matched_raw.get("score") if isinstance(matched_raw.get("score"), dict) else None
            scored_eval = CopyScoringService.evaluate_copy(
                headline=headline,
                body=body,
                cta=cta,
                hashtags=hashtags,
                platform_key=platform_key,
                ai_scores=ai_score_obj
            )

            processed_var = {
                "id": var_id,
                "label": var_label,
                "headline": headline,
                "body": body,
                "cta": cta,
                "hashtags": hashtags,
                "score": scored_eval,
                "strengths": scored_eval["strengths"],
                "suggestions": scored_eval["suggestions"]
            }

            processed_variations.append(processed_var)
            platform_scores.append(scored_eval["overall"])

        result_payload = {
            "platform": platform_name,
            "variations": processed_variations
        }

        return result_payload, platform_scores

    def _build_prompt(
        self,
        product_name: str,
        description: str,
        target_audience: str,
        p_config: Dict[str, Any],
        tone_name: str,
        tone_desc: str,
        angles: List[Dict[str, Any]]
    ) -> str:
        """Construct prompt for Groq model."""
        rules_str = "\n".join(f"- {r}" for r in p_config.get("rules", []))
        limits = p_config.get("character_limits", {})
        limits_str = ", ".join(f"{k}: {v} chars max" for k, v in limits.items())

        angles_str = ""
        for a in angles:
            angles_str += f"\n- Variation {a['id']} ({a['label']}): {a['directive']}"

        prompt = f"""Generate platform-specific advertising copy for the following product:

PRODUCT NAME: {product_name}
PRODUCT DESCRIPTION / BENEFITS: {description or 'High quality product/service'}
TARGET AUDIENCE: {target_audience or 'General consumers'}

PLATFORM: {p_config['name']} ({p_config['format']})
PLATFORM RULES & CHARACTER LIMITS:
{rules_str}
Character Limits: {limits_str}

SELECTED TONE: {tone_name}
TONE DESCRIPTION: {tone_desc}

VARIATION ANGLES TO GENERATE:{angles_str}

STRICT JSON OUTPUT FORMAT REQUIRED:
Return ONLY a JSON object formatted exactly as follows:
{{
  "platform": "{p_config['name']}",
  "variations": [
    {{
      "id": "A",
      "label": "Feature-Focused",
      "headline": "Headline under limit",
      "body": "Body text respecting character limit",
      "cta": "Call to action button label",
      "hashtags": ["#tag1", "#tag2"],
      "score": {{
        "headline_strength": 82,
        "clarity": 88,
        "emotional_appeal": 75,
        "cta_effectiveness": 90
      }}
    }}
  ]
}}
"""
        return prompt

    def _build_fallback_platform_result(
        self,
        platform_name: str,
        p_config: Dict[str, Any],
        angles: List[Dict[str, Any]],
        product_name: str,
        parse_err: str
    ) -> tuple[Dict[str, Any], List[float]]:
        """Fallback builder if AI JSON output fails completely."""
        variations = []
        scores = []
        platform_key = p_config["key"]

        for a in angles:
            headline = f"Discover {product_name} — {a['label']}"
            body = f"Experience top performance with {product_name}. Tailored to meet your needs effectively."
            cta = "Learn More"
            hashtags = ["#" + product_name.replace(" ", ""), "#AdCopy"] if p_config.get("hashtags_required") else []

            scored = CopyScoringService.evaluate_copy(
                headline=headline,
                body=body,
                cta=cta,
                hashtags=hashtags,
                platform_key=platform_key
            )

            variations.append({
                "id": a["id"],
                "label": a["label"],
                "headline": headline,
                "body": body,
                "cta": cta,
                "hashtags": hashtags,
                "score": scored,
                "strengths": scored["strengths"],
                "suggestions": scored["suggestions"]
            })
            scores.append(scored["overall"])

        result = {
            "platform": platform_name,
            "warning": f"AI response formatting error fallback: {parse_err}",
            "variations": variations
        }
        return result, scores
