from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from backend.extensions import db
from backend.models import User

# Checks JWT and role. We re read role from DB so blacklist works even if the token is still valid.

def role_required(*roles: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")

            # prefer DB role over whatever is stuck in the token
            try:
                user = db.session.get(User, int(get_jwt_identity()))
                if user is not None:
                    role = user.role
            except (TypeError, ValueError):
                pass

            if role == "blacklisted" or role not in roles:
                return (
                    jsonify(
                        {
                            "error": "Forbidden",
                            "message": "You do not have permission to access this resource.",
                            "status": 403,
                        }
                    ),
                    403,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
