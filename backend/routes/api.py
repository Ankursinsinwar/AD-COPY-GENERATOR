"""
Ad Copy Generator REST API Endpoints.

Defines API routes for:
- GET /api/health
- POST /api/generate
- POST /api/export/csv
- POST /api/export/notion
- GET /api/history
- GET /api/history/<id>
"""

from flask import Blueprint, request, jsonify, Response, current_app
from backend.utils.validators import validate_campaign_input
from backend.services.ad_generator import AdGeneratorService
from backend.services.history_service import HistoryService
from backend.services.export_service import ExportService
from backend.services.groq_service import GroqService

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Services instances (or instantiated per request / helper)
ad_generator_service = AdGeneratorService()
history_service = HistoryService()
export_service = ExportService()


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    groq_svc = GroqService()
    return jsonify({
        "status": "ok",
        "service": "Ad Copy Generator + A/B Tester API",
        "version": "1.0.0",
        "groq_configured": groq_svc.is_configured(),
        "model": groq_svc.model
    }), 200


@api_bp.route("/generate", methods=["POST"])
def generate_ad_copy():
    """
    Generate ad copy and A/B variations endpoint.
    Expects JSON payload with campaign settings.
    """
    data = request.get_json(silent=True) or {}
    
    # Input validation
    is_valid, error_msg, status_code = validate_campaign_input(data)
    if not is_valid:
        return jsonify({"error": error_msg, "status_code": status_code}), status_code

    product_name = str(data.get("product_name", "")).strip()
    description = str(data.get("description", "")).strip()
    target_audience = str(data.get("target_audience", "")).strip()
    platforms = data.get("platforms", [])
    if isinstance(platforms, str):
        platforms = [p.strip() for p in platforms.split(",") if p.strip()]
    tone = str(data.get("tone", "professional")).strip()
    variation_count = int(data.get("variation_count", 3))

    try:
        campaign = ad_generator_service.generate_campaign(
            product_name=product_name,
            description=description,
            target_audience=target_audience,
            platforms=platforms,
            tone=tone,
            variation_count=variation_count
        )
        return jsonify({"status": "success", "campaign": campaign}), 200
    except Exception as e:
        current_app.logger.error(f"Error during campaign generation: {e}")
        return jsonify({"error": f"Failed to generate campaign: {str(e)}", "status_code": 500}), 500


@api_bp.route("/export/csv", methods=["POST"])
def export_csv():
    """
    Export generated campaign results to CSV file.
    Expects campaign result payload in POST request.
    """
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No campaign data provided for CSV export", "status_code": 400}), 400

    campaign_data = data.get("campaign") or data
    csv_content = export_service.generate_csv(campaign_data)
    
    product_name = campaign_data.get("product_name") or campaign_data.get("product") or "campaign"
    safe_name = "".join(c for c in product_name if c.isalnum() or c in ("_", "-")).strip().lower() or "campaign"
    filename = f"{safe_name}_ad_copy.csv"

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@api_bp.route("/export/notion", methods=["POST"])
def export_notion():
    """
    Export generated campaign results to Notion-compatible Markdown.
    Expects campaign result payload in POST request.
    """
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No campaign data provided for Notion export", "status_code": 400}), 400

    campaign_data = data.get("campaign") or data
    markdown_content = export_service.generate_notion_markdown(campaign_data)

    return jsonify({
        "status": "success",
        "markdown": markdown_content,
        "product_name": campaign_data.get("product_name", "Campaign")
    }), 200


@api_bp.route("/history", methods=["GET"])
def get_history():
    """Get latest campaign generation history."""
    try:
        history = history_service.get_history(limit=20)
        return jsonify({"status": "success", "history": history}), 200
    except Exception as e:
        current_app.logger.error(f"Error reading history: {e}")
        return jsonify({"error": f"Failed to retrieve history: {str(e)}", "status_code": 500}), 500


@api_bp.route("/history/<campaign_id>", methods=["GET"])
def get_history_item(campaign_id: str):
    """Get a specific campaign entry by ID."""
    try:
        item = history_service.get_history_by_id(campaign_id)
        if not item:
            return jsonify({"error": f"Campaign '{campaign_id}' not found", "status_code": 404}), 404
        return jsonify({"status": "success", "campaign": item}), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching campaign {campaign_id}: {e}")
        return jsonify({"error": f"Failed to fetch campaign: {str(e)}", "status_code": 500}), 500
