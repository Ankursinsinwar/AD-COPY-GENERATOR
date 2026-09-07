"""
Automated unit tests for multi-stage JSON extraction parser.
"""

from backend.utils.json_parser import extract_json


def test_json_extraction_direct():
    """Method 1: Test direct json.loads extraction."""
    raw = '{"platform": "Google Ads", "status": "ok"}'
    ok, data, err = extract_json(raw)
    assert ok is True
    assert data["platform"] == "Google Ads"
    assert err == ""


def test_json_extraction_markdown():
    """Method 2: Test fenced ```json ... ``` markdown code block extraction."""
    raw = """Here is the generated ad copy response:
```json
{
  "platform": "Facebook",
  "variations": [{"id": "A", "headline": "Hook Line"}]
}
```
Hope this helps!"""
    ok, data, err = extract_json(raw)
    assert ok is True
    assert data["platform"] == "Facebook"
    assert data["variations"][0]["id"] == "A"


def test_json_extraction_generic_code_block():
    """Method 3: Test generic ``` ... ``` code block extraction."""
    raw = """
```
{
  "platform": "LinkedIn",
  "headline": "B2B SaaS Growth"
}
```
"""
    ok, data, err = extract_json(raw)
    assert ok is True
    assert data["platform"] == "LinkedIn"


def test_json_extraction_embedded_object():
    """Method 4: Test heuristic string scanning for embedded JSON objects in arbitrary text."""
    raw = """Certainly! Here is your requested copy in JSON format: {"platform": "Instagram", "score": 92} Enjoy your campaign!"""
    ok, data, err = extract_json(raw)
    assert ok is True
    assert data["platform"] == "Instagram"
    assert data["score"] == 92


def test_json_extraction_failure():
    """Test safe extraction failure handling when no valid JSON exists."""
    raw = "Sorry, I am unable to generate copy at this time due to high server load."
    ok, data, err = extract_json(raw)
    assert ok is False
    assert data is None
    assert "Failed to extract valid JSON" in err
