# Queue Celery jobs from the API (export CSV, admin reminder/report buttons).
from pathlib import Path

from celery.result import AsyncResult
from flask import Blueprint, current_app, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required

from backend.auth.decorators import role_required
from backend.auth.jwt_helpers import get_current_company, get_current_student
from backend.tasks import (
    export_applications_csv,
    send_daily_reminders,
    send_monthly_admin_report,
)


from backend.workers import celery

jobs_bp = Blueprint("jobs_api", __name__, url_prefix="/api/jobs")



def _task_status_payload(task_id: str) -> dict:
    result = AsyncResult(task_id, app=celery)
    payload = {"task_id": task_id, "state": result.state}
    if result.successful():
        payload["result"] = result.result
    elif result.failed():
        payload["error"] = str(result.result)
    return payload


@jobs_bp.get("/tasks/<task_id>")
@jwt_required()
def task_status(task_id):
    #ui polls this after starting an export
    return jsonify(_task_status_payload(task_id))


@jobs_bp.post("/exports/applications")
@jwt_required()
@role_required("student", "company")
def start_applications_export():
    data = request.get_json(silent=True) or {} # exports via email or download
    delivery = (data.get("delivery") or "download").strip().lower()
    if delivery not in ("download", "email", "both"):
        delivery = "download"

    student = get_current_student()
    company = get_current_company()

    if student:
        task = export_applications_csv.delay("student", student.id, delivery)
    elif company:
        task = export_applications_csv.delay("company", company.id, delivery)
    else:
        return jsonify({"error": "Not Found", "message": "Profile not found.", "status": 404}), 404

    return jsonify(
        {
            "message": "Export started.",
            "task_id": task.id,
            "delivery": delivery,
        }
    ), 202


@jobs_bp.get("/exports/<path:filename>")
@jwt_required()
@role_required("student", "company", "admin")
def download_export(filename):
    
    safe_name = Path(filename).name
    student = get_current_student()
    company = get_current_company()

    # filename starts with student_<id>_ or company_<id>_ so people can't grab others' CSVs
    if student and not safe_name.startswith(f"student_{student.id}_"):
        return jsonify({"error": "Forbidden", "message": "Not your export file.", "status": 403}), 403
    
    if company and not safe_name.startswith(f"company_{company.id}_"):
        return jsonify({"error": "Forbidden", "message": "Not your export file.", "status": 403}), 403

    exports_dir = Path(current_app.instance_path) / "exports"
    
    target = exports_dir / safe_name
    if not target.is_file():
        return jsonify({"error": "Not Found", "message": "Export file not found.", "status": 404}), 404
    return send_from_directory(exports_dir, safe_name, as_attachment=True)


@jobs_bp.post("/admin/daily-reminders")
@jwt_required()
@role_required("admin")
def trigger_daily_reminders():
    #manual endpoint to trigger reminder
    task = send_daily_reminders.delay()
    return jsonify({"message": "Daily reminders queued.", "task_id": task.id}), 202


@jobs_bp.post("/admin/monthly-report")
@jwt_required()
@role_required("admin")
def trigger_monthly_report():
    task = send_monthly_admin_report.delay()
    return jsonify({"message": "Monthly report queued.", "task_id": task.id}), 202
