from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from backend.auth.decorators import role_required
from backend.auth.utils import as_csv, clean, to_float, to_int
from backend.cache import (
    admin_dashboard_key,
    cached_json,
    invalidate_admin_caches,
    invalidate_job_related_caches,
    store_json,
)
from backend.extensions import bcrypt, db
from backend.models import Application, Company, JobPosition, Placement, Student, User
from backend.utils.parsers import job_position_from_json
from backend.utils.serializers import (
    serialize_application,
    serialize_company,
    serialize_job_position,
    serialize_placement,
    serialize_student,
)

admin_bp = Blueprint("admin_api", __name__, url_prefix="/api/admin")

# Admin API to approve companies, drives, blacklist/unblacklist students/companies and gather placement statistics
@admin_bp.get("/dashboard")
@jwt_required()
@role_required("admin")
def dashboard():
    # cached. bump admin_version when stats/lists change
    search_q = clean(request.args.get("q"))
    key = admin_dashboard_key(search_q)
    hit = cached_json(key) #Caching
    if hit:
        return hit

    stats = {
        "total_students": Student.query.count(),
        "total_companies": Company.query.count(),
        "total_job_positions": JobPosition.query.count(),
        "total_applications": Application.query.count(),
        "total_placements": Placement.query.count(),
    }

    pending_companies = Company.query.filter_by(approval_status="pending").all()
    pending_jobs = JobPosition.query.filter_by(approval_status="pending").all()

    # Using ilike for string search and match
    if search_q:
        students = (
            Student.query.join(User)
            .filter(
                (User.username.ilike(f"%{search_q}%"))
                | (Student.full_name.ilike(f"%{search_q}%"))
                | (User.email.ilike(f"%{search_q}%"))
            )
            .all()
        )
        companies = (
            Company.query.join(User)
            .filter(
                (Company.name.ilike(f"%{search_q}%")) | (Company.industry.ilike(f"%{search_q}%"))
            )
            .all()
        )
    else:
        students = Student.query.all()
        companies = Company.query.all()

    recent_applications = (
        Application.query.order_by(Application.applied_at.desc()).limit(10).all()
    )
    all_jobs = JobPosition.query.order_by(JobPosition.created_at.desc()).all()

    return store_json(
        key,
        {   "stats": stats,
            "pending_companies": [serialize_company(c, include_user=True) for c in pending_companies],
            "pending_job_positions": [serialize_job_position(j, include_company=True) for j in pending_jobs],
            "students": [serialize_student(s, include_user=True) for s in students],
            "companies": [serialize_company(c, include_user=True) for c in companies],
            "job_positions": [serialize_job_position(j, include_company=True) for j in all_jobs],
            "recent_applications": [serialize_application(a, include_details=True) for a in recent_applications],
            "search_q": search_q or None,
        },
    )


@admin_bp.get("/students/<int:student_id>")
@jwt_required()
@role_required("admin")
def student_detail(student_id):
    # modal: profile + applications
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"error": "Not Found", "message": "Student not found.", "status": 404}), 404

    applications = (
        Application.query.filter_by(student_id=student.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return jsonify(
        {
            "student": serialize_student(student, include_user=True),
            "applications": [serialize_application(a, include_details=True) for a in applications],
        }
    )


@admin_bp.get("/companies/<int:company_id>")
@jwt_required()
@role_required("admin")
def company_detail(company_id):
    # modal: company + per-drive applicant counts
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404

    drives = []
    for job in sorted(company.job_positions, key=lambda j: j.created_at or 0, reverse=True):
        apps = job.applications or []
        drives.append(
            {
                **serialize_job_position(job),
                "stats": {
                    "total_applications": len(apps),
                    "shortlisted": sum(1 for a in apps if a.status == "shortlisted"),
                    "selected": sum(1 for a in apps if a.status == "selected"),
                    "rejected": sum(1 for a in apps if a.status == "rejected"),
                    "applied": sum(1 for a in apps if a.status == "applied"),
                },
            }
        )

    return jsonify(
        {
            "company": serialize_company(company, include_user=True),
            "drives": drives,
            "stats": {
                "total_drives": len(drives),
                "total_applications": sum(d["stats"]["total_applications"] for d in drives),
                "total_selected": sum(d["stats"]["selected"] for d in drives),
            },
        }
    )


@admin_bp.get("/job-positions/<int:job_id>")
@jwt_required()
@role_required("admin")
def job_detail(job_id):
    # modal for one drive
    job = db.session.get(JobPosition, job_id)
    if not job:
        return jsonify({"error": "Not Found", "message": "Drive not found.", "status": 404}), 404

    apps = job.applications or []
    return jsonify(
        {
            "job_position": serialize_job_position(job, include_company=True),
            "stats": {
                "total_applications": len(apps),
                "shortlisted": sum(1 for a in apps if a.status == "shortlisted"),
                "selected": sum(1 for a in apps if a.status == "selected"),
                "rejected": sum(1 for a in apps if a.status == "rejected"),
                "applied": sum(1 for a in apps if a.status == "applied"),
            },
            "applications": [serialize_application(a, include_details=True) for a in apps],
        }
    )


@admin_bp.post("/companies/<int:company_id>/approve")
@jwt_required()
@role_required("admin")
def approve_company(company_id):
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404
    company.approval_status = "approved"
    db.session.commit()
    invalidate_job_related_caches()
    return jsonify({"message": "Company approved.", "company": serialize_company(company)})


@admin_bp.post("/companies/<int:company_id>/reject")
@jwt_required()
@role_required("admin")
def reject_company(company_id):
    company = db.session.get(Company, company_id)
    
    if not company:
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404
    
    company.approval_status = "rejected"
    db.session.commit()
    invalidate_job_related_caches()
    return jsonify({"message": "Company rejected.", "company": serialize_company(company)})


@admin_bp.post("/companies/<int:company_id>/blacklist")
@jwt_required()
@role_required("admin")
def blacklist_company(company_id):
    
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404
    
    
    company.approval_status = "rejected"
    company.user.role = "blacklisted"
    db.session.commit()
    invalidate_job_related_caches()
    
    return jsonify({"message": "Company blacklisted.", "company": serialize_company(company)})


@admin_bp.post("/companies/<int:company_id>/unblacklist")
@jwt_required()
@role_required("admin")
def unblacklist_company(company_id):
    # unblacklist company 
    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404
    if company.user.role != "blacklisted":
        return jsonify({"error": "Bad Request", "message": "Company is not blacklisted.", "status": 400}), 400

    company.user.role = "company"
    
    # Unblacking listing a company will again be required to go through approval process via admin
    company.approval_status = "pending"
    db.session.commit()
    invalidate_job_related_caches()
    invalidate_admin_caches()
    
    return jsonify({"message": "Company re-enabled. Approval set to pending.", "company": serialize_company(company, include_user=True)})


@admin_bp.post("/students/<int:student_id>/blacklist")
@jwt_required()
@role_required("admin")
def blacklist_student(student_id):
    
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"error": "Not Found", "message": "Student not found.", "status": 404}), 404
    student.user.role = "blacklisted"
    db.session.commit()
    
    invalidate_admin_caches() #invalidate admin cache since we are blacklisting 
    return jsonify({"message": "Student blacklisted.", "student": serialize_student(student, include_user=True)})


@admin_bp.post("/students/<int:student_id>/unblacklist")
@jwt_required()
@role_required("admin")
def unblacklist_student(student_id):
    
    # blacklist only changed user.role, so just set it back
    student = db.session.get(Student, student_id)
    
    if not student:
        return jsonify({"error": "Not Found", "message": "Student not found.", "status": 404}), 404
    if student.user.role != "blacklisted":
        return jsonify({"error": "Bad Request", "message": "Student is not blacklisted.", "status": 400}), 400

    student.user.role = "student"
    db.session.commit()
    invalidate_admin_caches() #same as blacklisting, can't use the same cache
    return jsonify({"message": "Student re-enabled.", "student": serialize_student(student, include_user=True)})


@admin_bp.post("/students")
@jwt_required()
@role_required("admin")
def add_student():
    '''
    Admin adding a student
    '''

    data = request.get_json(silent=True) or {}
    username = clean(data.get("username"))
    email = clean(data.get("email"))
    password = data.get("password") or ""
    full_name = clean(data.get("full_name"))

    if not all([username, email, password, full_name]):
        return jsonify({"error": "Bad Request", "message": "Required fields missing.", "status": 400}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Conflict", "message": "Username or email already exists.", "status": 409}), 409

    try:
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=hashed, role="student")
        db.session.add(user)
        db.session.flush()
        
        student = Student(
            user_id=user.id,
            full_name=full_name,
            phone=clean(data.get("phone")) or None,
            cgpa=to_float(data.get("cgpa")),
            graduation_year=to_int(data.get("graduation_year")),
            skills=as_csv(data.get("skills")),
        )
        
        
        db.session.add(student)
        db.session.commit()
        invalidate_admin_caches()
        return jsonify({"message": "Student added.", "student": serialize_student(student, include_user=True)}), 201
    
    except IntegrityError:
        
        db.session.rollback()
        return jsonify({"error": "Conflict", "message": "Could not add student.", "status": 409}), 409


@admin_bp.delete("/students/<int:student_id>")
@jwt_required()
@role_required("admin")
def delete_student(student_id):
    
    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({"error": "Not Found", "message": "Student not found.", "status": 404}), 404
    user = student.user
    
    try:
        db.session.delete(student)
        db.session.flush()
        db.session.delete(user)
        db.session.commit()
        invalidate_admin_caches()
        return jsonify({"message": "student Deleted"})
    
    except Exception:
        db.session.rollback()
        
        return jsonify({"error": "Bad Request", "message": "Could not delete student.", "status": 400}), 400


# admin altering companies
@admin_bp.post("/companies")
@jwt_required()
@role_required("admin")
def add_company():
    
    data = request.get_json(silent=True) or {}
    username = clean(data.get("username"))
    email = clean(data.get("email"))
    password = data.get("password") or ""
    company_name = clean(data.get("company_name"))

    if not all([username, email, password, company_name]):
        return jsonify({"error": "Bad Request", "message": "Required fields missing.", "status": 400}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "Conflict", "message": "Username or email already exists.", "status": 409}), 409
    if Company.query.filter_by(name=company_name).first():
        return jsonify({"error": "Conflict", "message": "Company name already exists.", "status": 409}), 409

    try:
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=hashed, role="company")
        db.session.add(user)
        db.session.flush()
        # admin-created companies skip the pending queue
        company = Company(
            user_id=user.id,
            name=company_name,
            website=clean(data.get("website")) or None,
            hr_contact=clean(data.get("hr_contact")) or None,
            industry=clean(data.get("industry")) or None,
            approval_status="approved",
        )
        
        db.session.add(company)
        db.session.commit()
        invalidate_job_related_caches()
        return jsonify({"message": "Company added and approved.", "company": serialize_company(company, include_user=True)}), 201
    
    except IntegrityError:
        
        db.session.rollback()
        return jsonify({"error": "Conflict", "message": "Could not add company.", "status": 409}), 409


@admin_bp.delete("/companies/<int:company_id>")
@jwt_required()
@role_required("admin")
def delete_company(company_id):
    
    company = db.session.get(Company, company_id)
    if not company:
        
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404
    
    user = company.user
    
    try:
        db.session.delete(company)
        db.session.flush()
        db.session.delete(user)
        db.session.commit()
        invalidate_job_related_caches()
        return jsonify({"message": "Company deleted."})
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Bad Request", "message": "Could not delete company.", "status": 400}), 400

# admin actions : approval/rejection of companies
@admin_bp.post("/job-positions/<int:job_id>/approve")
@jwt_required()
@role_required("admin")
def approve_job(job_id):
    job = db.session.get(JobPosition, job_id)
    if not job:
        return jsonify({"error": "Not Found", "message": "Job position not found.", "status": 404}), 404
    
    job.approval_status = "approved"
    db.session.commit()
    invalidate_job_related_caches()
    
    return jsonify({"message": "Job position approved.", "job_position": serialize_job_position(job, include_company=True)})


@admin_bp.post("/job-positions/<int:job_id>/reject")
@jwt_required()
@role_required("admin")
def reject_job(job_id):
    
    job = db.session.get(JobPosition, job_id)
    if not job:
        return jsonify({"error": "Not Found", "message": "Job position not found.", "status": 404}), 404
    
    job.approval_status = "rejected"
    db.session.commit()
    invalidate_job_related_caches()
    
    return jsonify({"message": "Job position rejected.", "job_position": serialize_job_position(job, include_company=True)})


@admin_bp.post("/job-positions")
@jwt_required()
@role_required("admin")
def add_job():
    
    data = request.get_json(silent=True) or {}
    company_id = to_int(data.get("company_id"))
    fields = job_position_from_json(data)

    if not company_id or not fields["title"]:
        return jsonify({"error": "Bad Request", "message": "company_id and title are required.", "status": 400}), 400

    company = db.session.get(Company, company_id)
    if not company:
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404

    job = JobPosition(
        company_id=company_id,
        **fields,
        status="active",
        approval_status="approved",
    )
    
    db.session.add(job)
    db.session.commit()
    invalidate_job_related_caches()
    return jsonify({"message": "Job position created.", "job_position": serialize_job_position(job, include_company=True)}), 201


@admin_bp.delete("/job-positions/<int:job_id>")
@jwt_required()
@role_required("admin")
def delete_job(job_id):
    
    job = db.session.get(JobPosition, job_id)
    if not job:
        return jsonify({"error": "Not Found", "message": "Job position not found.", "status": 404}), 404
    
    try:
        db.session.delete(job)
        db.session.commit()
        invalidate_job_related_caches()
        return jsonify({"message": "Job position deleted."})
    
    except Exception:
        
        db.session.rollback()
        return jsonify({"error": "Bad Request", "message": "Could not delete job position.", "status": 400}), 400


@admin_bp.get("/placements")
@jwt_required()
@role_required("admin")
def list_placements():
    
    # admin placements tab: add names so the table is readable
    placements = Placement.query.order_by(Placement.placed_at.desc()).all()
    rows = []
    
    for p in placements:
        row = serialize_placement(p)
        row["student_name"] = p.student.full_name if p.student else None
        row["company_name"] = p.company.name if p.company else None
        job = p.application.job_position if p.application else None
        row["job_title"] = job.title if job else None
        rows.append(row)
        
    return jsonify({"placements": rows})
