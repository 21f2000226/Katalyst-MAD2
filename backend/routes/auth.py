
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from backend.auth.decorators import role_required
from backend.auth.utils import as_csv, clean, jwt_claims_for_user, serialize_user, to_float, to_int
from backend.cache import invalidate_admin_caches
from backend.extensions import bcrypt, db
from backend.models import Company, Student, User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Authentication routes-  login, register,and refresh.
@auth_bp.post("/login")
def login():
    
    data = request.get_json(silent=True) or {}
    identifier = clean(data.get("username") or data.get("email"))
    password = data.get("password") or ""

    if not identifier or not password:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Username/email and password are required.",
                    "status": 400,
                }
            ),
            400,
        )

    user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
    
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return (
            jsonify(
                {
                    "error": "Unauthorized",
                    "message": "Invalid username/email or password.",
                    "status": 401,
                }
            ),
            401,
        )

    #blacklisted users shouldn't be able log in at all
    if user.role == "blacklisted":
        return (
            jsonify(
                {
                    "error": "Forbidden",
                    "message": "This account has been blacklisted.",
                    "status": 403,
                }
            ),
            403,
        )
        

    claims = jwt_claims_for_user(user)
    access_token = create_access_token(identity=str(user.id), additional_claims=claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=claims)

    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "user": serialize_user(user),
        }
    )


@auth_bp.post("/register")
def register():
    
    data = request.get_json(silent=True) or {}
    role = clean(data.get("role")).lower()
    username = clean(data.get("username"))
    email = clean(data.get("email"))
    password = data.get("password") or ""
    password_confirm = data.get("password_confirm") or password

    if role not in ("student", "company"):
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Role must be either 'student' or 'company'.",
                    "status": 400,
                }
            ),
            400,
        )

    if not all([username, email, password]):
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Username, email, and password are required.",
                    "status": 400,
                }
            ),
            400,
        )

    if len(password) < 6:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Password must be at least 6 characters.",
                    "status": 400,
                }
            ),
            400,
        )

    if password != password_confirm:
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Passwords do not match.",
                    "status": 400,
                }
            ),
            400,
        )

    if User.query.filter_by(username=username).first():
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": "Username already exists.",
                    "status": 409,
                }
            ),
            409,
        )

    if User.query.filter_by(email=email).first():
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": "Email already exists.",
                    "status": 409,
                }
            ),
            409,
        )

    if role == "student":
        full_name = clean(data.get("full_name"))
        if not full_name:
            return (
                jsonify(
                    {
                        "error": "Bad Request",
                        "message": "Full name is required for student registration.",
                        "status": 400,
                    }
                ),
                400,
            )
    else:
        company_name = clean(data.get("company_name"))
        if not company_name:
            return (
                jsonify(
                    {
                        "error": "Bad Request",
                        "message": "Company name is required for company registration.",
                        "status": 400,
                    }
                ),
                400,
            )

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.session.add(user)
        db.session.flush()  # need user.id before creating profile row

        if role == "student":
            db.session.add(
                Student(
                    user_id=user.id,
                    full_name=clean(data.get("full_name")),
                    phone=clean(data.get("phone")) or None,
                    cgpa=to_float(data.get("cgpa")),
                    graduation_year=to_int(data.get("graduation_year")),
                    skills=as_csv(data.get("skills")),
                )
            )
        else:
            # companies start pending until admin approves
            db.session.add(
                Company(
                    user_id=user.id,
                    name=clean(data.get("company_name")),
                    website=clean(data.get("website")) or None,
                    hr_contact=clean(data.get("hr_contact")) or None,
                    industry=clean(data.get("industry")) or None,
                    approval_status="pending",
                )
            )
            

        db.session.commit()
        user = db.session.get(User, user.id)
        # so admin dashboard shows the new account
        invalidate_admin_caches()
        
        return (
            jsonify(
                {
                    "message": "Registration successful. Please log in.",
                    "user": serialize_user(user),
                }
            ),
            201,
        )
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": "User already exists or invalid data provided.",
                    "status": 409,
                }
            ),
            409,
        )


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "User not found.",
                    "status": 404,
                }
            ),
            404,
        )
    return jsonify({"user": serialize_user(user)})


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    # needs a refresh token, returns a new access token
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return (
            jsonify(
                {
                    "error": "Not Found",
                    "message": "User not found.",
                    "status": 404,
                }
            ),
            404,
        )

    claims = jwt_claims_for_user(user)
    access_token = create_access_token(identity=str(user.id), additional_claims=claims)
    
    return jsonify({"access_token": access_token, "token_type": "Bearer"})
