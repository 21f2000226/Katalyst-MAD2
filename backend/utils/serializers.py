from datetime import date, datetime

from backend.models import Application, Company, JobPosition, Placement, Student, User

# Turn db model objects into plain dicts for jsonift

def _dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _d(value: date | None) -> str | None:
    return value.isoformat() if value else None


def serialize_user_brief(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }


def serialize_student(student: Student, include_user: bool = False) -> dict:
    data = {
        "id": student.id,
        "full_name": student.full_name,
        "phone": student.phone,
        "cgpa": student.cgpa,
        "graduation_year": student.graduation_year,
        "skills": student.skills,
        "resume_path": student.resume_path,
        "notify_deadlines": bool(student.notify_deadlines),
        "created_at": _dt(student.created_at),
    }
    if include_user and student.user:
        data["user"] = serialize_user_brief(student.user)
    return data


def serialize_company(company: Company, include_user: bool = False) -> dict:
    data = {
        "id": company.id,
        "name": company.name,
        "website": company.website,
        "hr_contact": company.hr_contact,
        "industry": company.industry,
        "approval_status": company.approval_status,
        "created_at": _dt(company.created_at),
    }
    if include_user and company.user:
        data["user"] = serialize_user_brief(company.user)
    return data


def serialize_job_position(job: JobPosition, include_company: bool = False) -> dict:
    data = {
        "id": job.id,
        "company_id": job.company_id,
        "title": job.title,
        "description": job.description,
        "requirements": job.requirements,
        "min_cgpa": job.min_cgpa,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "deadline": _dt(job.deadline),
        "status": job.status,
        "approval_status": job.approval_status,
        "created_at": _dt(job.created_at),
    }
    if include_company and job.company:
        data["company"] = serialize_company(job.company)
    return data


def serialize_application(app: Application, include_details: bool = False) -> dict:
    data = {
        "id": app.id,
        "student_id": app.student_id,
        "job_position_id": app.job_position_id,
        "status": app.status,
        "interview_at": _dt(app.interview_at),
        "interview_notes": app.interview_notes,
        "applied_at": _dt(app.applied_at),
        "updated_at": _dt(app.updated_at),
    }
    if include_details:
        if app.student:
            data["student"] = serialize_student(app.student, include_user=True)
        if app.job_position:
            data["job_position"] = serialize_job_position(app.job_position, include_company=True)
        if app.placement:
            data["placement"] = serialize_placement(app.placement)
    return data


def serialize_placement(placement: Placement) -> dict:
    return {
        "id": placement.id,
        "application_id": placement.application_id,
        "student_id": placement.student_id,
        "company_id": placement.company_id,
        "salary": placement.salary,
        "joining_date": _d(placement.joining_date),
        "placed_at": _dt(placement.placed_at),
        "created_at": _dt(placement.created_at),
    }
