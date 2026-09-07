"""
Multi-method JSON extraction utility with fallbacks.

Attempts to parse raw LLM responses into structured Python data using
four distinct extraction strategies to ensure reliability against variable model formatting.
"""

import json
import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


def extract_json(raw_response: str) -> Tuple[bool, Any, str]:
    """
    Extract and parse JSON from raw text using 4 multi-stage fallback methods.
    
    Args:
        raw_response (str): The raw string output from the LLM.
        
    Returns:
        Tuple[bool, Any, str]: 
            - bool: True if extraction succeeded, False otherwise.
            - Any: Parsed JSON data (dict or list) if successful, None or error dict if failed.
            - str: Error message or empty string on success.
    """
    if not raw_response or not isinstance(raw_response, str):
        return False, None, "Raw response is empty or not a string"

    text = raw_response.strip()

    # METHOD 1: Direct json.loads
    try:
        data = json.loads(text)
        return True, data, ""
    except (json.JSONDecodeError, TypeError):
        pass

    # METHOD 2: Fenced ```json ... ``` blocks
    json_block_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
    if json_block_match:
        try:
            block_content = json_block_match.group(1).strip()
            data = json.loads(block_content)
            return True, data, ""
        except json.JSONDecodeError:
            pass

    # METHOD 3: Generic ``` ... ``` blocks
    generic_block_matches = re.findall(r'```\s*(.*?)\s*```', text, re.DOTALL)
    for block in generic_block_matches:
        cleaned_block = block.strip()
        # Skip if it starts with a non-json lang like 'python' or 'html'
        if cleaned_block.lower().startswith(("python", "bash", "html", "javascript", "css")):
            continue
        try:
            data = json.loads(cleaned_block)
            return True, data, ""
        except json.JSONDecodeError:
            pass

    # METHOD 4: Heuristic/decoder scanning for embedded JSON objects or arrays
    # Find first '{' or '[' and match to corresponding closing brace/bracket
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start_idx = text.find(start_char)
        while start_idx != -1:
            end_idx = text.rfind(end_char)
            while end_idx > start_idx:
                candidate = text[start_idx:end_idx + 1]
                try:
                    data = json.loads(candidate)
                    return True, data, ""
                except json.JSONDecodeError:
                    # Retry with shorter substring ending at previous occurrence
                    end_idx = text.rfind(end_char, start_idx, end_idx)
            start_idx = text.find(start_char, start_idx + 1)

    # All methods failed
    error_msg = "Failed to extract valid JSON after trying all 4 parsing fallback methods."
    logger.warning(error_msg + f" Raw snippet: {text[:150]}")
    return False, None, error_msg
