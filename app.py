"""
Ad Copy Generator + A/B Tester — Main Application Factory Entry Point.

Architectural Principles:
- Modular Application Factory pattern (create_app).
- Enables CORS for API endpoints.
- Serves modern single-page SaaS frontend from frontend/ index.html.
- Registers API Blueprint (/api/*) and handles errors gracefully.
"""

import os
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Base directory setup
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def create_app(config_name=None):
    """
    Application Factory for Flask.
    
    Args:
        config_name (str): Configuration environment name ('development', 'testing', 'production').
                           If None, defaults to FLASK_ENV env var or 'development'.
    
    Returns:
        Flask: Configured Flask application instance.
    """
    frontend_dir = BASE_DIR / "frontend"
    app = Flask(__name__, static_folder=str(frontend_dir), static_url_path="")

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-12345")
    app.config["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY", "")
    app.config["GROQ_MODEL"] = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
    app.config["EXPORTS_DIR"] = BASE_DIR / "exports"
    app.config["DATA_DIR"] = BASE_DIR / "data"

    if config_name == "testing":
        app.config["TESTING"] = True
    elif config_name == "development" or os.environ.get("FLASK_ENV") == "development":
        app.config["DEBUG"] = True

    # Ensure required directories exist
    os.makedirs(app.config["EXPORTS_DIR"], exist_ok=True)
    os.makedirs(app.config["DATA_DIR"], exist_ok=True)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API Blueprints
    from backend.routes.api import api_bp
    app.register_blueprint(api_bp)

    # Serve Frontend UI
    @app.route("/")
    def index():
        """Serve the main frontend index.html single-page app."""
        if (frontend_dir / "index.html").exists():
            return send_from_directory(str(frontend_dir), "index.html")
        return jsonify({"message": "Ad Copy Generator API is online. Frontend UI missing."}), 200

    @app.route("/<path:path>")
    def static_proxy(path):
        """Serve frontend static assets."""
        file_path = frontend_dir / path
        if file_path.exists() and not file_path.is_dir():
            return send_from_directory(str(frontend_dir), path)
        # Fallback to index.html for SPA routing if needed
        if (frontend_dir / "index.html").exists():
            return send_from_directory(str(frontend_dir), "index.html")
        return jsonify({"error": "File not found", "status_code": 404}), 404

    # Register Centralized Error Handlers
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """Register HTTP error handlers for JSON API and web requests."""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": getattr(error, "description", "Bad Request"),
            "status_code": 400
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "error": "Resource or endpoint not found",
                "status_code": 404
            }), 404
        return jsonify({"error": "Page not found", "status_code": 404}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal Server Error: {error}")
        return jsonify({
            "error": "Internal server error occurred",
            "status_code": 500
        }), 500


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
