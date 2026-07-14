
from flask import jsonify
from flask_jwt_extended.exceptions import JWTExtendedException
from werkzeug.exceptions import HTTPException

# Turn JWT or HTTP errors into the same JSON shape the Vue app expects.
def register_error_handlers(app):
    from backend.extensions import jwt

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": "Token has expired.",
                    "status": 401,
                }
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": str(error),
                    "status": 401,
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": str(error),
                    "status": 401,
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_payload):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": "Token has been revoked.",
                    "status": 401,
                }
            ),
            401,
        )

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exception(error):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": str(error),
                    "status": 401,
                }
            ),
            401,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        return (
            jsonify(
                {
                    "error": error.name,
                    "message": error.description,
                    "status": error.code,
                }
            ),
            error.code,
        )

    @app.errorhandler(404)
    def handle_not_found(error):
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "The requested resource was not found.",
                    "status": 404,
                }
            ),
            404,
        )

    @app.errorhandler(500)
    def handle_internal_error(error):
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                    "status": 500,
                }
            ),
            500,
        )
