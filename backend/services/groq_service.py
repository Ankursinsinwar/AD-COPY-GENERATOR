"""
Groq AI API Integration Service.

Manages communication with the Groq API using the Llama 3.1 8B Instant model.
Handles initialization, API calls, rate limits (HTTP 429), and errors gracefully.
"""

import os
import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)


class GroqService:
    """Service wrapper for Groq AI API interaction."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Groq service.
        
        Args:
            api_key (Optional[str]): Groq API key.
            model (Optional[str]): Model identifier.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.model = model or os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        self.client = None

        if self.api_key and self.api_key.strip() and not self.api_key.startswith("your_"):
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Groq SDK client initialization deferred: {e}")

    def is_configured(self) -> bool:
        """Check if Groq client is configured with a valid API key."""
        return self.client is not None or (bool(self.api_key) and not self.api_key.startswith("your_"))

    def generate_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Send completion request to Groq API.
        
        Args:
            system_prompt (str): System instruction prompt.
            user_prompt (str): User prompt containing context and formatting rules.
            temperature (float): Sampling temperature.
            
        Returns:
            Tuple[bool, str, Dict[str, Any]]: (success, raw_text_response, metadata)
                metadata contains keys: 'error', 'is_quota_exceeded', 'error_type'
        """
        meta = {"error": "", "is_quota_exceeded": False, "error_type": ""}

        if not self.is_configured():
            meta["error"] = "Groq API key is not configured. Please set GROQ_API_KEY in your environment."
            meta["error_type"] = "CONFIG_ERROR"
            return False, "", meta

        try:
            if not self.client:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=1500
            )

            raw_text = response.choices[0].message.content or ""
            return True, raw_text, meta

        except Exception as e:
            err_str = str(e)
            logger.error(f"Groq API call failed: {err_str}")
            
            if "429" in err_str or "quota" in err_str.lower() or "rate_limit" in err_str.lower():
                meta["is_quota_exceeded"] = True
                meta["error"] = "Groq API rate limit or quota exceeded (HTTP 429). Please try again later."
                meta["error_type"] = "QUOTA_EXCEEDED"
            else:
                meta["error"] = f"Groq API Error: {err_str}"
                meta["error_type"] = "API_ERROR"

            return False, "", meta
