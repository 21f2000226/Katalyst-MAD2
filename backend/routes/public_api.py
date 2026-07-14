# Public endpoints (requires no login). detail go through Redis cache.
from flask import Blueprint, jsonify, request

from backend.auth.utils import clean
from backend.cache import (
    cached_json,
    public_company_detail_key,
    public_job_detail_key,
    public_jobs_list_key,
    store_json,
)

from backend.extensions import db
from backend.models import Company, JobPosition
from backend.utils.serializers import serialize_company, serialize_job_position

public_bp = Blueprint("public_api", __name__, url_prefix="/api/public")


@public_bp.get("/job-positions")
def list_jobs():
    # only approved and  active drives. key includes search query so each query caches separately
    search_q = clean(request.args.get("q"))
    key = public_jobs_list_key(search_q)
    hit = cached_json(key)
    
    if hit:
        return hit

    query = JobPosition.query.filter_by(status="active", approval_status="approved")
    
    if search_q:
        query = query.filter(
            (JobPosition.title.ilike(f"%{search_q}%"))
            | (JobPosition.description.ilike(f"%{search_q}%"))
            | (JobPosition.requirements.ilike(f"%{search_q}%"))
        )

    jobs = query.order_by(JobPosition.created_at.desc()).all()
    
    return store_json(
        key,
        {
            "job_positions": [serialize_job_position(j, include_company=True) for j in jobs],
            "search_q": search_q or None,
        },
    )


@public_bp.get("/job-positions/<int:job_id>")
def job_detail(job_id):
    
    key = public_job_detail_key(job_id)
    hit = cached_json(key)
    if hit:
        return hit

    job = db.session.get(JobPosition, job_id)
    if not job or job.status != "active" or job.approval_status != "approved":
        return jsonify({"error": "Not Found", "message": "Job not found.", "status": 404}), 404

    return store_json(key, {"job_position": serialize_job_position(job, include_company=True)})


@public_bp.get("/companies/<int:company_id>")
def company_detail(company_id):
    key = public_company_detail_key(company_id)
    hit = cached_json(key)
    if hit:
        return hit

    company = db.session.get(Company, company_id)
    if not company or company.approval_status != "approved":
        return jsonify({"error": "Not Found", "message": "Company not found.", "status": 404}), 404

    active_jobs = [
        j for j in company.job_positions if j.status == "active" and j.approval_status == "approved"
    ]
    
    return store_json(
        key,
        {
            "company": serialize_company(company),
            "job_positions": [serialize_job_position(j) for j in active_jobs],
        },
    )
