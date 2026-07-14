# App factory. Builds the Flask app and wires extensions + blueprints.
import os

from flask import Flask
from flask_cors import CORS

from backend.config import DevConfig
from backend.errors import register_error_handlers
from backend.extensions import bcrypt, db, flask_cache, jwt
from backend.routes import register_blueprints


def create_app(config_class=DevConfig):
    # put sqlite under backend/instance so it stays with the API
    backend_dir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(backend_dir, "instance")
    app = Flask(
        __name__,
        instance_relative_config=True,
        instance_path=instance_path,
    )
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = config_class.sqlite_uri(app.instance_path)

    # resume uploads go here
    upload_folder = os.path.join(app.root_path, "static", "resumes")
    upload_folder = os.path.abspath(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = upload_folder

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    # Redis cache (CACHE_REDIS_URL from config)
    flask_cache.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": os.environ.get("CORS_ORIGINS", "*")}},
        supports_credentials=False,
    )

    register_error_handlers(app)
    register_blueprints(app)

    # quick check that Redis is alive (demo / health)
    @app.get("/api/cache/health")
    def cache_health():
        info = {
            "redis_url": app.config.get("CACHE_REDIS_URL"),
            "container": app.config.get("REDIS_CONTAINER_NAME"),
        }
        try:
            flask_cache.set("katalyst:healthcheck", "ok", timeout=10)
            ok = flask_cache.get("katalyst:healthcheck") == "ok"
            info["redis"] = "ok" if ok else "error"
            return info, (200 if ok else 503)
        except Exception as exc:
            info["redis"] = "error"
            info["message"] = str(exc)
            return info, 503

    # if frontend/dist exists, serve the built Vue app on the same port
    _register_spa_routes(app)

    return app


def _register_spa_routes(app: Flask) -> None:
    # catch-all for SPA. API routes are registered first so they still win.
    from flask import send_from_directory

    dist_dir = os.path.abspath(os.path.join(app.root_path, "..", "frontend", "dist"))
    if not os.path.isdir(dist_dir):
        return

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_vue_spa(path: str):
        # don't let the SPA eat /api or /health
        if path.startswith("api/") or path == "health":
            return {"error": "Not Found", "message": "Unknown endpoint.", "status": 404}, 404
        candidate = os.path.join(dist_dir, path)
        if path and os.path.isfile(candidate):
            return send_from_directory(dist_dir, path)
        return send_from_directory(dist_dir, "index.html")
