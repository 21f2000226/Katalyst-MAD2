# Create tables + default admin if db is missing.
# no migrations present ! ayooo - possible future
import os

from backend.extensions import bcrypt, db
from backend.models import User

DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@placement.local")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password123")


def initialize_database(seed_admin: bool = True) -> None:
    db.create_all()

    if not seed_admin:
        return

    existing_admin = User.query.filter_by(role="admin").first()
    if existing_admin:
        return

    admin = User(
        username=DEFAULT_ADMIN_USERNAME,
        email=DEFAULT_ADMIN_EMAIL,
        password_hash=bcrypt.generate_password_hash(DEFAULT_ADMIN_PASSWORD).decode("utf-8"),
        role="admin",
    )
    db.session.add(admin)
    db.session.commit()
