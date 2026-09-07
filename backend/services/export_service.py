"""
CSV & Notion Markdown Export Helper Service.

Generates downloadable CSV spreadsheets and Notion-compatible Markdown documents
from campaign results.
"""

import csv
import io
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

logger = logging.getLogger(__name__)

# Base directory for file exports
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXPORTS_DIR = BASE_DIR / "exports"


class ExportService:
    """Service for converting campaign data to CSV and Notion Markdown formats."""

    def __init__(self, exports_dir: Optional[Path] = None):
        """
        Initialize export service.
        
        Args:
            exports_dir (Optional[Path]): Directory where generated export files are saved.
        """
        self.exports_dir = exports_dir or EXPORTS_DIR
        os.makedirs(self.exports_dir, exist_ok=True)

    def generate_csv(self, campaign_data: Dict[str, Any]) -> str:
        """
        Generate CSV string from campaign results.
        
        CSV Headers:
        Platform, Variation, Label, Headline, Body, CTA, Hashtags, Overall Score, Suggestions
        """
        output = io.StringIO()
        fieldnames = [
            "Platform",
            "Variation",
            "Label",
            "Headline",
            "Body",
            "CTA",
            "Hashtags",
            "Overall Score",
            "Suggestions"
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        rows = self._extract_flat_rows(campaign_data)
        for row in rows:
            writer.writerow(row)

        return output.getvalue()

    def generate_notion_markdown(self, campaign_data: Dict[str, Any]) -> str:
        """
        Generate Notion-compatible Markdown from campaign results.
        """
        product_name = campaign_data.get("product_name") or campaign_data.get("product") or "Ad Campaign"
        tone = campaign_data.get("tone", "").capitalize()
        audience = campaign_data.get("target_audience") or campaign_data.get("audience") or ""

        md = []
        md.append(f"# {product_name} — Ad Campaign\n")
        if tone:
            md.append(f"**Tone:** {tone}")
        if audience:
            md.append(f"**Target Audience:** {audience}")
        md.append("\n---\n")

        results = campaign_data.get("results", {})
        if isinstance(results, list):
            # Convert list format to dict grouped by platform if needed
            new_results = {}
            for item in results:
                p_name = item.get("platform", "Platform")
                if p_name not in new_results:
                    new_results[p_name] = []
                new_results[p_name].extend(item.get("variations", [item]))
            results = new_results

        for platform_name, variations in results.items():
            md.append(f"## {platform_name}\n")
            if isinstance(variations, dict) and "variations" in variations:
                variations = variations.get("variations", [])

            if isinstance(variations, list):
                for v in variations:
                    v_id = v.get("id", "A")
                    label = v.get("label", "Variation")
                    headline = v.get("headline", "")
                    body = v.get("body", v.get("description", ""))
                    cta = v.get("cta", "")
                    hashtags = v.get("hashtags", [])
                    if isinstance(hashtags, list):
                        hashtags_str = " ".join(hashtags)
                    else:
                        hashtags_str = str(hashtags or "")

                    score_data = v.get("score", {})
                    if isinstance(score_data, dict):
                        overall_score = score_data.get("overall", score_data.get("overall_performance", 0))
                    else:
                        overall_score = score_data or 0

                    strengths = v.get("strengths", [])
                    suggestions = v.get("suggestions", [])

                    md.append(f"### Variation {v_id} — {label}\n")
                    md.append(f"**Headline**\n{headline}\n")
                    md.append(f"**Body**\n{body}\n")
                    md.append(f"**CTA**\n{cta}\n")
                    if hashtags_str:
                        md.append(f"**Hashtags**\n{hashtags_str}\n")
                    md.append(f"**Score**\n{overall_score}/100\n")

                    if strengths:
                        md.append("**Strengths**")
                        for s in strengths:
                            md.append(f"- {s}")
                        md.append("")

                    if suggestions:
                        md.append("**Suggestions**")
                        for s in suggestions:
                            md.append(f"- {s}")
                        md.append("")

                    md.append("")

        return "\n".join(md).strip()

    def export_csv_file(self, campaign_data: Dict[str, Any], filename: str = "campaign_export.csv") -> Path:
        """Save CSV string to file in exports_dir."""
        csv_content = self.generate_csv(campaign_data)
        file_path = self.exports_dir / filename
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            f.write(csv_content)
        return file_path

    def export_notion_file(self, campaign_data: Dict[str, Any], filename: str = "campaign_export.md") -> Path:
        """Save Notion Markdown to file in exports_dir."""
        md_content = self.generate_notion_markdown(campaign_data)
        file_path = self.exports_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        return file_path

    def _extract_flat_rows(self, campaign_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Flatten nested campaign results into dictionary rows for CSV writer."""
        rows = []
        results = campaign_data.get("results", {})

        if isinstance(results, list):
            new_results = {}
            for item in results:
                p_name = item.get("platform", "Platform")
                if p_name not in new_results:
                    new_results[p_name] = []
                new_results[p_name].extend(item.get("variations", [item]))
            results = new_results

        for platform_name, variations in results.items():
            if isinstance(variations, dict) and "variations" in variations:
                variations = variations.get("variations", [])

            if isinstance(variations, list):
                for v in variations:
                    score_data = v.get("score", {})
                    overall = score_data.get("overall", 0) if isinstance(score_data, dict) else score_data
                    hashtags = v.get("hashtags", [])
                    hashtags_str = " ".join(hashtags) if isinstance(hashtags, list) else str(hashtags or "")
                    suggestions = v.get("suggestions", [])
                    suggestions_str = " | ".join(suggestions) if isinstance(suggestions, list) else str(suggestions or "")

                    rows.append({
                        "Platform": platform_name,
                        "Variation": v.get("id", "A"),
                        "Label": v.get("label", ""),
                        "Headline": v.get("headline", ""),
                        "Body": v.get("body", v.get("description", "")),
                        "CTA": v.get("cta", ""),
                        "Hashtags": hashtags_str,
                        "Overall Score": str(overall),
                        "Suggestions": suggestions_str
                    })
        return rows
