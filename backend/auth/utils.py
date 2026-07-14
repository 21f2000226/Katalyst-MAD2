from backend.models import User

#Authentiction helpers to clean input form fields , buildig JSON's and JWT


def clean(value: str | None) -> str:
    return (value or "").strip()


def as_csv(value: str | None) -> str | None:
    cleaned = clean(value)
    
    if not cleaned:
        return None
    items = [item.strip() for item in cleaned.split(",") if item.strip()]
    
    return ", ".join(items) if items else None


def to_float(value) -> float | None:
    
    if value is None or value == "":
        return None
    try:
        return float(value)
    
    except (TypeError, ValueError):
        return None


def to_int(value) -> int | None:
    
    if value is None or value == "":
        return None
    
    try:
        return int(value)
    
    except (TypeError, ValueError):
        return None


def serialize_user(user: User) -> dict:
    '''
    Serializes details before adding into DB, useful for maintaining consitency
    '''
    payload = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

    if user.student:
        payload["student"] = {
            "id": user.student.id,
            "full_name": user.student.full_name,
            "phone": user.student.phone,
            "cgpa": user.student.cgpa,
            "graduation_year": user.student.graduation_year,
            "skills": user.student.skills,
            "resume_path": user.student.resume_path,
        }

    if user.company:
        payload["company"] = {
            "id": user.company.id,
            "name": user.company.name,
            "website": user.company.website,
            "hr_contact": user.company.hr_contact,
            "industry": user.company.industry,
            "approval_status": user.company.approval_status,
        }

    return payload


def jwt_claims_for_user(user: User) -> dict:
    '''
    Check role from JWT
    '''
    claims = {"role": user.role}
    if user.student:
        claims["student_id"] = user.student.id
    if user.company:
        claims["company_id"] = user.company.id
    return claims
