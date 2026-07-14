# /health for a quick "is the API up" check
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

#health endpoint
@health_bp.get("/health")
def health_check():
    return jsonify({"status": "ok", "service": "katalyst-api"})
