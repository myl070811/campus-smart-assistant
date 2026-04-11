"""
校园智慧助手 — Flask 入口。

运行: python app.py
开发环境默认 http://127.0.0.1:5000
"""

from pathlib import Path
import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from data.db import db
from data.migrate import run_migrations
from data.seed import ensure_demo_extensions, seed_if_empty
from routes import register_routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "campus-smart-assistant-demo-secret")
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///campus_assistant.db",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {
                "origins": [
                    "http://127.0.0.1:5173",
                    "http://localhost:5173",
                    "http://127.0.0.1",
                    "http://localhost",
                ]
            }
        },
    )
    db.init_app(app)

    with app.app_context():
        db.create_all()
        run_migrations()
        seed_if_empty()
        ensure_demo_extensions()

    register_routes(app)

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "campus-smart-assistant"
        })

    @app.get("/api/files/awards/<path:filename>")
    def get_award_file(filename: str):
        folder = Path(__file__).resolve().parent / "uploads" / "awards"
        return send_from_directory(folder, filename, as_attachment=False)

    @app.get("/api/files/org-logos/<path:filename>")
    def get_org_logo_file(filename: str):
        folder = Path(__file__).resolve().parent / "uploads" / "org-logos"
        return send_from_directory(folder, filename, as_attachment=False)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)