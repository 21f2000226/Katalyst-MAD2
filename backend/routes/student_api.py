# Student API: browse drives, apply, profile, resume upload.
import os
import uuid

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from backend.auth.decorators import role_required
from backend.auth.jwt_helpers import get_current_student
from backend.auth.utils import as_csv, clean, to_float, to_int
from backend.extensions import db
from backend.models import Application, Company, JobPosition, Placement
from backend.utils.serializers import (
    serialize_application,
    serialize_company,
    serialize_job_position,
    serialize_placement,
    serialize_student,
)

student_bp = Blueprint("student_api", __name__, url_prefix="/api/student")

ALLOWED_RESUME_EXTS = {"pdf", "doc", "docx"}


def _allowed_resume(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_RESUME_EXTS


@student_bp.get("/dashboard")
@jwt_required()
@role_required("student")
def dashboard():
    student = get_current_student()
    if not student:
        return jsonify({"error": "Not Found", "message": "Student profile not found.", "status": 404}), 404

    available_jobs = (
        JobPosition.query.filter_by(status="active", approval_status="approved")
        .order_by(JobPosition.created_at.desc())
        .all()
    )
    applied_job_ids = {app.job_position_id for app in student.applications}
    applications = (
        Application.query.filter_by(student_id=student.id)
        .order_by(Application.applied_at.desc())
        .all()
    )

    # first placement we find (student shouldn't have more than one)
    placement = None
    for app in applications:
        if app.placement:
            placement = app.placement
            break

    return jsonify(
        {
            "student": serialize_student(student),
            "available_job_positions": [serialize_job_position(j, include_company=True) for j in available_jobs],
            "applied_job_position_ids": list(applied_job_ids),
            "applications": [serialize_application(a, include_details=True) for a in applications],
            "placement": serialize_placement(placement) if placement else None,
        }
    )


@student_bp.get("/profile")
@jwt_required()
@role_required("student")
def get_profile():
    
    student = get_current_student()
    if not student:
        return jsonify({"error": "Not Found", "message": "Student profile not found.", "status": 404}), 404
    return jsonify({"student": serialize_student(student, include_user=True)})


@student_bp.put("/profile")
@jwt_required()
@role_required("student")
def update_profile():
    
    student = get_current_student()
    if not student:
        return jsonify({"error": "Not Found", "message": "Student profile not found.", "status": 404}), 404

    data = request.get_json(silent=True) or {}
    full_name = clean(data.get("full_name"))
    if not full_name:
        return jsonify({"error": "Bad Request", "message": "Full name is required.", "status": 400}), 400

    student.full_name = full_name
    student.phone = clean(data.get("phone")) or None
    student.skills = as_csv(data.get("skills"))
    student.cgpa = to_float(data.get("cgpa"))
    student.graduation_year = to_int(data.get("graduation_year"))
    
    # opt out of daily deadline emails if they want
    if "notify_deadlines" in data:
        student.notify_deadlines = bool(data.get("notify_deadlines")) # need to wire to UI

    db.session.commit()
    return jsonify({"message": "Profile updated.", "student": serialize_student(student)})


@student_bp.post("/applications")
@jwt_required()
@role_required("student")
def apply():
    # Student applies to an open, approved drive (job_position_id in body).
    student = get_current_student()
    data = request.get_json(silent=True) or {}
    job_id = to_int(data.get("job_position_id"))

    if not job_id:
        return jsonify({"error": "Bad Request", "message": "job_position_id is required.", "status": 400}), 400

    job = db.session.get(JobPosition, job_id)
    if not job or job.status != "active" or job.approval_status != "approved":
        return jsonify({"error": "Bad Request", "message": "Job is not open for applications.", "status": 400}), 400

    # check CGPA eligibility before applying
    if job.min_cgpa is not None:
        if student.cgpa is None:
            return (
                jsonify(
                    {
                        "error": "Bad Request",
                        "message": f"This drive requires CGPA >= {job.min_cgpa}. Add your CGPA in Profile first.",
                        "status": 400,
                    }
                ),
                400,
            )
        if float(student.cgpa) < float(job.min_cgpa):
            return (
                jsonify(
                    {
                        "error": "Forbidden",
                        "message": (
                            f"Not eligible: your CGPA ({student.cgpa}) is below "
                            f"the cutoff ({job.min_cgpa})."
                        ),
                        "status": 403,
                    }
                ),
                403,
            )

    existing = Application.query.filter_by(student_id=student.id, job_position_id=job_id).first()

    if existing:
        return jsonify({"error": "Conflict", "message": "Already applied to this job.", "status": 409}), 409

    try:
        application = Application(student_id=student.id, job_position_id=job_id, status="applied")
        db.session.add(application)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": f"Applied to '{job.title}'.",
                    "application": serialize_application(application, include_details=True),
                }
            ),
            201,
        )

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflict", "message": "Already applied to this job.", "status": 409}), 409


@student_bp.delete("/applications/<int:application_id>")
@jwt_required()
@role_required("student")
def withdraw(application_id):
    
    student = get_current_student()
    application = db.session.get(Application, application_id)
    
    if not application or application.student_id != student.id:
        return jsonify({"error": "Not Found", "message": "Application not found.", "status": 404}), 404

    if application.status != "applied":
        return (
            jsonify(
                {
                    "error": "Bad Request",
                    "message": "Only applications in 'applied' status can be withdrawn.",
                    "status": 400,
                }
            ),
            400,
        )

    db.session.delete(application)
    db.session.commit()
    
    return jsonify({"message": "Application withdrawn."})


@student_bp.get("/companies/<int:company_id>")
@jwt_required()
@role_required("student")
def view_company(company_id):
    student = get_current_student()
    company = db.session.get(Company, company_id)
    
    if not company or company.approval_status != "approved":
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404

    active_jobs = [
        j for j in company.job_positions if j.status == "active" and j.approval_status == "approved"
    ]
    applied_job_ids = {app.job_position_id for app in student.applications}

    return jsonify(
        {
            "company": serialize_company(company),
            "job_positions": [serialize_job_position(j) for j in active_jobs],
            "applied_job_position_ids": list(applied_job_ids),
        }
    )


@student_bp.get("/job-positions/<int:job_id>")
@jwt_required()
@role_required("student")
def view_job(job_id):
    
    student = get_current_student()
    job = db.session.get(JobPosition, job_id)
    
    if not job or job.status != "active" or job.approval_status != "approved":
        return jsonify({"error": "Not Found", "message": "Job not available.", "status": 404}), 404

    already_applied = (
        Application.query.filter_by(student_id=student.id, job_position_id=job_id).first() is not None
    )
    
    eligible = True
    eligibility_message = None
    if job.min_cgpa is not None:
        if student.cgpa is None:
            eligible = False
            eligibility_message = (
                f"This drive requires CGPA >= {job.min_cgpa}. Add your CGPA in Profile first."
            )
        elif float(student.cgpa) < float(job.min_cgpa):
            eligible = False
            eligibility_message = (
                f"Not eligible: your CGPA ({student.cgpa}) is below the cutoff ({job.min_cgpa})."
            )

    return jsonify(
        {
            "job_position": serialize_job_position(job, include_company=True),
            "already_applied": already_applied,
            "student_cgpa": student.cgpa,
            "eligible": eligible,
            "eligibility_message": eligibility_message,
        }
    )


@student_bp.post("/resume")
@jwt_required()
@role_required("student")
def upload_resume():
    student = get_current_student()
    
    if "resume" not in request.files:
        return jsonify({"error": "Bad Request", "message": "No file provided.", "status": 400}), 400

    file = request.files["resume"]
    
    if not file or file.filename == "":
        return jsonify({"error": "Bad Request", "message": "No file selected.", "status": 400}), 400
    
    if not _allowed_resume(file.filename):
        return jsonify({"error": "Bad Request", "message": "Only PDF, DOC, DOCX allowed.", "status": 400}), 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    # random name so uploads are always unique
    
    unique_name = f"student_{student.id}_{uuid.uuid4().hex[:8]}.{ext}"
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)

    # delete old file if they re-upload
    if student.resume_path:
        old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], student.resume_path)
        if os.path.exists(old_path):
            os.remove(old_path)

    file.save(save_path)
    student.resume_path = unique_name
    db.session.commit()
    return jsonify({"message": "Resume uploaded.", "resume_path": unique_name})


@student_bp.get("/resume")
@jwt_required()
@role_required("student")
def view_resume():
    student = get_current_student()
    if not student.resume_path:
        return jsonify({"error": "Not Found", "message": "No resume uploaded.", "status": 404}), 404
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], student.resume_path, as_attachment=False)


@student_bp.delete("/resume")
@jwt_required()
@role_required("student")
def delete_resume():
    
    student = get_current_student()
    if not student.resume_path:
        return jsonify({"error": "Not Found", "message": "No resume to delete.", "status": 404}), 404

    old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], student.resume_path)
    if os.path.exists(old_path):
        os.remove(old_path)

    student.resume_path = None
    db.session.commit()
    return jsonify({"message": "Resume deleted."})
