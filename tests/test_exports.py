"""
Automated unit tests for CSV and Notion Markdown Export Service.
"""

import csv
import io
from backend.services.export_service import ExportService


def test_csv_export(temp_dirs):
    """Test generating CSV output and verifying required headers and columns."""
    export_svc = ExportService(exports_dir=temp_dirs["exports"])

    sample_campaign = {
        "product_name": "Cloud CRM",
        "tone": "professional",
        "results": {
            "Instagram": {
                "variations": [
                    {
                        "id": "A",
                        "label": "Feature-Focused",
                        "headline": "Boost CRM Productivity",
                        "body": "Manage contacts instantly with cloud sync.",
                        "cta": "Start Free Trial",
                        "hashtags": ["#crm", "#cloud"],
                        "score": {"overall": 87.5},
                        "suggestions": ["Add power words"]
                    }
                ]
            }
        }
    }

    csv_str = export_svc.generate_csv(sample_campaign)
    reader = list(csv.reader(io.StringIO(csv_str)))
    assert len(reader) >= 2
    headers = reader[0]

    required_headers = [
        "Platform", "Variation", "Label", "Headline", "Body", "CTA", "Hashtags", "Overall Score", "Suggestions"
    ]
    for rh in required_headers:
        assert rh in headers

    row = reader[1]
    assert "Instagram" in row
    assert "Boost CRM Productivity" in row
    assert "87.5" in row


def test_notion_markdown_export(temp_dirs):
    """Test generating Notion-compatible Markdown format."""
    export_svc = ExportService(exports_dir=temp_dirs["exports"])

    sample_campaign = {
        "product_name": "Cloud CRM",
        "tone": "professional",
        "target_audience": "Sales Directors",
        "results": {
            "Instagram": {
                "variations": [
                    {
                        "id": "A",
                        "label": "Feature-Focused",
                        "headline": "Boost CRM Productivity",
                        "body": "Manage contacts instantly.",
                        "cta": "Start Trial",
                        "hashtags": ["#crm"],
                        "score": {"overall": 87.5},
                        "strengths": ["Clear CTA"],
                        "suggestions": ["Add power words"]
                    }
                ]
            }
        }
    }

    md_str = export_svc.generate_notion_markdown(sample_campaign)
    assert "# Cloud CRM — Ad Campaign" in md_str
    assert "## Instagram" in md_str
    assert "### Variation A — Feature-Focused" in md_str
    assert "**Headline**" in md_str
    assert "Boost CRM Productivity" in md_str
    assert "**Score**" in md_str
    assert "87.5/100" in md_str
    assert "**Strengths**" in md_str
    assert "**Suggestions**" in md_str
