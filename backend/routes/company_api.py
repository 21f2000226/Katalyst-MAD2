from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from backend.auth.decorators import role_required
from backend.auth.jwt_helpers import get_current_company
from backend.auth.utils import to_float
from backend.cache import invalidate_admin_caches, invalidate_job_related_caches
from backend.extensions import db
from backend.models import Application, JobPosition, Placement, Student
from backend.utils.parsers import job_position_from_json, parse_interview_at, parse_joining_date
from backend.utils.serializers import (
    serialize_application,
    serialize_company,
    serialize_job_position,
    serialize_placement,
    serialize_student,
)

# Company API's for drives, applicants, shortlisting/selecting students, and resume view.

company_bp = Blueprint("company_api", __name__, url_prefix="/api/company")


def _require_company():
    company = get_current_company()
    
    if not company:
        return None, (jsonify({"error": "Not Found", "message": "Company profile not found.", "status": 404}), 404)
    return company, None


@company_bp.get("/dashboard")
@jwt_required()
@role_required("company")
def dashboard():
    
    company, err = _require_company()
    if err:
        return err

    approved = [j for j in company.job_positions if j.approval_status == "approved"]
    pending = [j for j in company.job_positions if j.approval_status == "pending"]
    rejected = [j for j in company.job_positions if j.approval_status == "rejected"]

    total_applications = sum(len(j.applications) for j in company.job_positions)
    
    total_shortlisted = sum(
        sum(1 for a in j.applications if a.status == "shortlisted") for j in company.job_positions
    )
    total_selected = sum(
        sum(1 for a in j.applications if a.status == "selected") for j in company.job_positions
    )

    return jsonify(
        {
            "company": serialize_company(company),
            "stats": {
                "total_applications": total_applications,
                "total_shortlisted": total_shortlisted,
                "total_selected": total_selected,
            },
            "approved_job_positions": [serialize_job_position(j) for j in approved],
            "pending_job_positions": [serialize_job_position(j) for j in pending],
            "rejected_job_positions": [serialize_job_position(j) for j in rejected],
        }
    )


@company_bp.get("/profile")
@jwt_required()
@role_required("company")
def get_profile():
    
    company, err = _require_company()
    if err:
        return err
    return jsonify({"company": serialize_company(company, include_user=True)})


@company_bp.put("/profile")
@jwt_required()
@role_required("company")
def update_profile():
    # Company profile update
    from backend.auth.utils import clean # lazy loading

    company, err = _require_company()
    if err:
        return err

    data = request.get_json(silent=True) or {}
    name = clean(data.get("name") or data.get("company_name"))
    if not name:
        return jsonify({"error": "Bad Request", "message": "Company name is required.", "status": 400}), 400

    company.name = name
    company.website = clean(data.get("website")) or None
    company.hr_contact = clean(data.get("hr_contact")) or None
    company.industry = clean(data.get("industry")) or None

    try:
        #checks if company with such a name already exists, if error rollbacks the db
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Conflict",
                    "message": "That company name is already taken.",
                    "status": 409,
                }
            ),
            409,
        )

    invalidate_job_related_caches()
    invalidate_admin_caches()
    
    return jsonify({"message": "Profile updated.", "company": serialize_company(company, include_user=True)})


@company_bp.post("/job-positions")
@jwt_required()
@role_required("company")
def create_job():
    company, err = _require_company()
    if err:
        return err

    if company.approval_status != "approved":
        return (
            jsonify(
                {
                    "error": "Forbidden",
                    "message": "Company must be approved before posting jobs.",
                    "status": 403,
                }
            ),
            403,
        )

    data = request.get_json(silent=True) or {}
    fields = job_position_from_json(data)
    if not fields["title"]:
        return jsonify({"error": "Bad Request", "message": "Title is required.", "status": 400}), 400

    job = JobPosition(
        company_id=company.id,
        **fields,
        status="active",
        approval_status="pending",
    )
    
    db.session.add(job)
    db.session.commit()
    # pending job still shows on admin dashboard
    
    invalidate_job_related_caches()
    return (
        jsonify(
            {
                "message": "Job position submitted for admin approval.",
                "job_position": serialize_job_position(job),
            }
        ),
        201,
    )


@company_bp.put("/job-positions/<int:job_id>")
@jwt_required()
@role_required("company")
def edit_job(job_id):
    #edit existing drive/job, on edit, requires admin approval again. 
    company, err = _require_company()
    if err:
        return err
    job = db.session.get(JobPosition, job_id)
    if not job or job.company_id != company.id:
        return jsonify({"error": "Not Found", "message": "Job position not found.", "status": 404}), 404

    data = request.get_json(silent=True) or {}
    fields = job_position_from_json(data)
    if not fields["title"]:
        return jsonify({"error": "Bad Request", "message": "Title is required.", "status": 400}), 400

    was_approved = job.approval_status == "approved"
    job.title = fields["title"]
    job.description = fields["description"]
    job.requirements = fields["requirements"]
    job.min_cgpa = fields["min_cgpa"]
    job.salary_min = fields["salary_min"]
    job.salary_max = fields["salary_max"]
    job.deadline = fields["deadline"]

    # if they edit a live drive, send it back to pending for approval
    if was_approved:
        job.approval_status = "pending"

    db.session.commit()
    
    invalidate_job_related_caches()
    invalidate_admin_caches()
    
    message = (
        "Drive updated and re-submitted for admin approval."
        if was_approved
        else "Drive updated."
    )
    return jsonify({"message": message, "job_position": serialize_job_position(job)})


@company_bp.post("/job-positions/<int:job_id>/toggle")
@jwt_required()
@role_required("company")
def toggle_job(job_id):
    # 'close' means students can't apply. 'reopen' needs admin again
    company, err = _require_company()
    
    if err:
        return err
    job = db.session.get(JobPosition, job_id)
    
    if not job or job.company_id != company.id:
        return jsonify({"error": "Not Found", "message": "Drive not found.", "status": 404}), 404

    if job.status == "active":
        job.status = "closed"
        db.session.commit()
        invalidate_job_related_caches()
        return jsonify(
            {
                "message": "Drive closed. Students can no longer apply.",
                "job_position": serialize_job_position(job),
            }
        )

    # reopened but will be kept pending until admin approves
    job.status = "active"
    job.approval_status = "pending"
    db.session.commit()
    
    invalidate_job_related_caches()
    invalidate_admin_caches()
    
    return jsonify(
        {
            "message": "Reopen requested. An admin must approve this drive again before it goes live.",
            "job_position": serialize_job_position(job),
        }
    )


@company_bp.delete("/job-positions/<int:job_id>")
@jwt_required()
@role_required("company")
def delete_job(job_id):
    
    company, err = _require_company()
    if err:
        return err
    job = db.session.get(JobPosition, job_id)
    if not job or job.company_id != company.id:
        return jsonify({"error": "Not Found", "message": "Job position not found.", "status": 404}), 404

    try:
        
        db.session.delete(job)
        db.session.commit()
        invalidate_job_related_caches()
        return jsonify({"message": "Job position deleted."})
    except Exception:
        
        db.session.rollback()
        return jsonify({"error": "Bad Request", "message": "Could not delete job.", "status": 400}), 400


@company_bp.get("/job-positions/<int:job_id>")
@jwt_required()
@role_required("company")
def job_detail(job_id):
    
    company, err = _require_company()
    
    if err:
        return err
    job = db.session.get(JobPosition, job_id)
    if not job or job.company_id != company.id:
        return jsonify({"error": "Not Found", "message": "Job position not found.", "status": 404}), 404

    applications = (
        Application.query.filter_by(job_position_id=job_id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    
    return jsonify(
        {
            "job_position": serialize_job_position(job),
            "applications": [serialize_application(a, include_details=True) for a in applications],
        }
    )


@company_bp.patch("/applications/<int:application_id>/status")
@jwt_required()
@role_required("company")
def update_application_status(application_id):
    # shortlist / reject / select applicants. select will also create a row un placement table.
    from backend.tasks import _send_email

    company, err = _require_company()
    
    if err:
        return err
    application = db.session.get(Application, application_id)
    
    if not application or application.job_position.company_id != company.id:
        return jsonify({"error": "Not Found", "message": "Application not found.", "status": 404}), 404

    data = request.get_json(silent=True) or {}
    new_status = (data.get("status") or "").strip()
    allowed = ("applied", "shortlisted", "selected", "rejected")

    if new_status not in allowed:
        return jsonify({"error": "Bad Request", "message": "Invalid status.", "status": 400}), 400

    old_status = application.status
    application.status = new_status

    # interview time/notes only make sense on shortlist
    emailed = False
    if new_status == "shortlisted":
        
        if "interview_at" in data:
            application.interview_at = parse_interview_at(data.get("interview_at"))
        if "interview_notes" in data:
            application.interview_notes = (data.get("interview_notes") or "").strip() or None
            
    elif new_status in ("rejected", "applied"):
        application.interview_at = None
        application.interview_notes = None

    # On selection input salary (LPA) for the Placement record
    if new_status == "selected" and not application.placement:
        salary = to_float(data.get("salary"))
        if salary is None:
            return (
                jsonify(
                    {
                        "error": "Bad Request",
                        "message": "salary (LPA) is required when selecting a candidate.",
                        "status": 400,
                    }
                ),
                400,
            )
            
        db.session.add(
            Placement(
                application_id=application.id,
                student_id=application.student_id,
                company_id=company.id,
                salary=salary,
                joining_date=parse_joining_date(data.get("joining_date")),
            )
        )
        
    elif old_status == "selected" and new_status != "selected" and application.placement:
        db.session.delete(application.placement)

    try:
        db.session.commit()
        invalidate_admin_caches()
        application = db.session.get(Application, application_id)
        
        # mail the student right away (MailHog in local demo)
        if new_status == "shortlisted" and application.student and application.student.user:
            
            job = application.job_position
            when = (
                application.interview_at.strftime("%Y-%m-%d %H:%M UTC")
                if application.interview_at
                else "To be confirmed"
            )
            
            notes_html = application.interview_notes or "None"
            html = f"""
            <p>Hi {application.student.full_name},</p>
            <p>You have been <strong>shortlisted</strong> for
            <strong>{job.title if job else 'a drive'}</strong>
            at <strong>{company.name}</strong>.</p>
            <p><strong>Interview:</strong> {when}</p>
            <p><strong>Notes:</strong> {notes_html}</p>
            """
            
            emailed = _send_email(
                subject=f"Shortlisted: {job.title if job else 'Placement drive'}",
                html_body=html,
                to_addr=application.student.user.email,
            )

        return jsonify(
            {
                "message": f"Application status updated to '{new_status}'.",
                "emailed": emailed,
                "application": serialize_application(application, include_details=True),
            }
        )
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflict", "message": "Could not update application.", "status": 409}), 409


@company_bp.get("/students/<int:student_id>/resume")
@jwt_required()
@role_required("company")
def view_student_resume(student_id):
    
    company, err = _require_company()
    
    if err:
        return err
    student = db.session.get(Student, student_id)
    
    if not student:
        return jsonify({"error": "Not Found", "message": "Student not found.", "status": 404}), 404

    # only resumes of people who applied to our drives
    company_job_ids = {j.id for j in company.job_positions}
    student_job_ids = {a.job_position_id for a in student.applications}
    
    if not company_job_ids.intersection(student_job_ids):
        return (
            jsonify(
                {
                    "error": "Forbidden",
                    "message": "You can only view resumes of your applicants.",
                    "status": 403,
                }
            ),
            403,
        )

    if not student.resume_path:
        return jsonify({"error": "Not Found", "message": "Student has no resume.", "status": 404}), 404

    return send_from_directory(current_app.config["UPLOAD_FOLDER"], student.resume_path, as_attachment=False)