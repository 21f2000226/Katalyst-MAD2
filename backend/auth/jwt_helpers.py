from flask_jwt_extended import get_jwt_identity

from backend.extensions import db
from backend.models import Company, Student, User

# Load user via JWt, no recurring authentication or authorization requests 
# will hit the server

def get_current_user() -> User | None:
    user_id = int(get_jwt_identity())
    return db.session.get(User, user_id)


def get_current_student() -> Student | None:
    user = get_current_user()
    if not user or user.role != "student":
        return None
    return user.student


def get_current_company() -> Company | None:
    user = get_current_user()
    if not user or user.role != "company":
        return None
    return user.company
