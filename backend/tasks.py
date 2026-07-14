# Celery tasks: daily reminders, monthly report, CSV export.
import csv
import smtplib
from datetime import datetime, timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from backend.workers import celery, flask_app


def _project_instance_dir() -> Path:
    app = flask_app()
    path = Path(app.instance_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _log_reminder(title: str, body: str) -> dict:
    # append to instance/logs/reminders.log (no chat webhook)
    logs_dir = _project_instance_dir() / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "reminders.log"
    stamp = datetime.utcnow().isoformat()
    with open(log_file, "a", encoding="utf-8") as handle:
        handle.write(f"[{stamp}] {title}\n{body}\n\n")
    return {"logged_to": str(log_file), "email": False}


def _send_email(
    subject: str,
    html_body: str,
    to_addr: str,
    attachment_path: str | None = None,
    attachment_name: str | None = None,
) -> bool:
    # returns false if SMTP_HOST blank or send fails (task will still continue)
    app = flask_app()
    host = app.config.get("SMTP_HOST") or ""
    if not host or not to_addr:
        return False

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = app.config.get("SMTP_FROM")
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html"))

    if attachment_path:
        path = Path(attachment_path)
        if path.is_file():
            part = MIMEApplication(path.read_bytes(), Name=attachment_name or path.name)
            part["Content-Disposition"] = f'attachment; filename="{attachment_name or path.name}"'
            msg.attach(part)

    port = int(app.config.get("SMTP_PORT") or 587)
    user = app.config.get("SMTP_USER") or ""
    password = app.config.get("SMTP_PASSWORD") or ""
    use_tls = bool(app.config.get("SMTP_USE_TLS"))

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            if use_tls:
                server.starttls()
            if user:
                server.login(user, password)
            server.sendmail(msg["From"], [to_addr], msg.as_string())
        return True
    except (smtplib.SMTPException, OSError, TimeoutError) as exc:
        # don't crash the whole Celery job if mail is down
        logs_dir = _project_instance_dir() / "logs"
        logs_dir.mkdir(exist_ok=True)
        stamp = datetime.utcnow().isoformat()
        with open(logs_dir / "smtp.log", "a", encoding="utf-8") as handle:
            handle.write(f"[{stamp}] SMTP failed to {to_addr}: {exc}\n")
        return False


@celery.task(name="backend.tasks.send_daily_reminders")
def send_daily_reminders():
    # for deadlines in 3 days interviews in 2 days + admin summary
    from backend.models import Application, JobPosition, Student

    app = flask_app()
    with app.app_context():
        now = datetime.utcnow()
        soon = now + timedelta(days=3)
        interview_horizon = now + timedelta(days=2)

        closing_jobs = JobPosition.query.filter(
            JobPosition.status == "active",
            JobPosition.approval_status == "approved",
            JobPosition.deadline.isnot(None),
            JobPosition.deadline >= now,
            JobPosition.deadline <= soon,
        ).all()

        pending_apps = Application.query.filter_by(status="applied").count()
        lines = [
            f"Jobs closing within 3 days: {len(closing_jobs)}",
            f"Applications still in 'applied' status: {pending_apps}",
        ]
        for job in closing_jobs[:10]:
            deadline = job.deadline.date().isoformat() if job.deadline else "?"
            lines.append(f"- {job.title} (deadline {deadline})")

        body = "\n".join(lines)
        delivery = _log_reminder("Katalyst daily reminder", body)

        students_emailed = 0
        interview_emails = 0

        # only students who left notify_deadlines on
        opted_in = Student.query.filter_by(notify_deadlines=True).all()
        for student in opted_in:
            if not student.user or not student.user.email:
                continue
            applied_ids = {a.job_position_id for a in student.applications}
            open_for_student = [j for j in closing_jobs if j.id not in applied_ids]
            if not open_for_student:
                continue
            items = "".join(
                f"<li><strong>{j.title}</strong> at {j.company.name if j.company else '?'} "
                f"(deadline {j.deadline.strftime('%Y-%m-%d') if j.deadline else '?'})</li>"
                for j in open_for_student
            )
            html = (
                f"<p>Hi {student.full_name},</p>"
                f"<p>These approved placement drives close within 3 days:</p>"
                f"<ul>{items}</ul>"
                f"<p>You can turn these emails off in your profile.</p>"
            )
            if _send_email(
                subject="Katalyst: upcoming drive deadlines",
                html_body=html,
                to_addr=student.user.email,
            ):
                students_emailed += 1

        upcoming_interviews = Application.query.filter(
            Application.status == "shortlisted",
            Application.interview_at.isnot(None),
            Application.interview_at >= now,
            Application.interview_at <= interview_horizon,
        ).all()
        for item in upcoming_interviews:
            student = item.student
            job = item.job_position
            if not student or not student.user or not student.user.email:
                continue
            when = item.interview_at.strftime("%Y-%m-%d %H:%M UTC")
            company_name = job.company.name if job and job.company else "the company"
            html = (
                f"<p>Hi {student.full_name},</p>"
                f"<p>Reminder: your interview for <strong>{job.title if job else 'a drive'}</strong> "
                f"at <strong>{company_name}</strong> is scheduled for <strong>{when}</strong>.</p>"
                f"<p>Notes: {item.interview_notes or 'None'}</p>"
            )
            if _send_email(
                subject=f"Interview reminder: {job.title if job else 'placement drive'}",
                html_body=html,
                to_addr=student.user.email,
            ):
                interview_emails += 1

        # admin always gets a summary (good for demos)
        admin_html = f"<pre style='font-family: system-ui, sans-serif;'>{body}</pre>"
        delivery["email"] = _send_email(
            subject="Katalyst daily reminder (admin summary)",
            html_body=admin_html,
            to_addr=app.config.get("ADMIN_EMAIL"),
        )
        delivery["students_emailed"] = students_emailed
        delivery["interview_emails"] = interview_emails
        return {"ok": True, "summary": body, "delivery": delivery}


@celery.task(name="backend.tasks.send_monthly_admin_report")
def send_monthly_admin_report():
    # HTML file under instance/reports/ or email if SMTP is set
    from backend.models import Application, Company, JobPosition, Placement, Student

    app = flask_app()
    with app.app_context():
        
        now = datetime.utcnow()
        month_label = now.strftime("%B %Y")
        stats = {
            "students": Student.query.count(),
            "companies": Company.query.count(),
            "job_positions": JobPosition.query.count(),
            "applications": Application.query.count(),
            "placements": Placement.query.count(),
            "pending_companies": Company.query.filter_by(approval_status="pending").count(),
            "pending_jobs": JobPosition.query.filter_by(approval_status="pending").count(),
        }
        

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Katalyst Monthly Report</title></head>
<body style="font-family: system-ui, sans-serif; padding: 1.5rem;">
  <h1>Katalyst monthly activity report</h1>
  <p>Period snapshot: <strong>{month_label}</strong> (generated {now.isoformat()} UTC)</p>
  <ul>
    <li>Students: {stats['students']}</li>
    <li>Companies: {stats['companies']}</li>
    <li>Job positions: {stats['job_positions']}</li>
    <li>Applications: {stats['applications']}</li>
    <li>Placements: {stats['placements']}</li>
    <li>Pending companies: {stats['pending_companies']}</li>
    <li>Pending jobs: {stats['pending_jobs']}</li>
  </ul>
</body></html>
"""

        reports_dir = _project_instance_dir() / "reports"
        reports_dir.mkdir(exist_ok=True)
        filename = f"monthly_report_{now.strftime('%Y_%m')}.html"
        report_path = reports_dir / filename
        report_path.write_text(html, encoding="utf-8")

        emailed = _send_email(
            subject=f"Katalyst monthly report - {month_label}",
            html_body=html,
            to_addr=app.config.get("ADMIN_EMAIL"),
        )
        
        _log_reminder(
            "Katalyst monthly report ready",
            f"Saved to {report_path}. Email sent: {emailed}",
        )
        
        return {
            "ok": True,
            "report_path": str(report_path),
            "emailed": emailed,
            "stats": stats,
        }


@celery.task(name="backend.tasks.export_applications_csv")
def export_applications_csv(role: str, owner_id: int, delivery: str = "download"):
    # role might be student|company. delivery via download|email|both
    from backend.extensions import db
    from backend.models import Application, Company, JobPosition, Student

    delivery = (delivery or "download").strip().lower()
    if delivery not in ("download", "email", "both"):
        delivery = "download"

    app = flask_app()
    with app.app_context():
        exports_dir = _project_instance_dir() / "exports"
        exports_dir.mkdir(exist_ok=True)
        rows = []
        recipient = None

        if role == "student":
            student = db.session.get(Student, owner_id)
            if not student:
                return {"ok": False, "error": "Student not found"}
            recipient = student.user.email if student.user else None
            apps = (
                Application.query.filter_by(student_id=student.id)
                .order_by(Application.applied_at.desc())
                .all()
            )
            for item in apps:
                job = item.job_position
                rows.append(
                    {
                        "application_id": item.id,
                        "job_title": job.title if job else "",
                        "company": job.company.name if job and job.company else "",
                        "status": item.status,
                        "interview_at": item.interview_at.isoformat() if item.interview_at else "",
                        "applied_at": item.applied_at.isoformat() if item.applied_at else "",
                    }
                )
            prefix = f"student_{owner_id}"

        elif role == "company":
            company = db.session.get(Company, owner_id)
            if not company:
                return {"ok": False, "error": "Company not found"}
            recipient = company.user.email if company.user else None
            apps = (
                Application.query.join(JobPosition)
                .filter(JobPosition.company_id == company.id)
                .order_by(Application.applied_at.desc())
                .all()
            )
            
            for item in apps:
                student = item.student
                job = item.job_position
                
                rows.append(
                    {
                        "application_id": item.id,
                        "job_title": job.title if job else "",
                        "student": student.full_name if student else "",
                        "email": student.user.email if student and student.user else "",
                        "status": item.status,
                        "interview_at": item.interview_at.isoformat() if item.interview_at else "",
                        "applied_at": item.applied_at.isoformat() if item.applied_at else "",
                    }
                )
                
            prefix = f"company_{owner_id}"
        else:
            return {"ok": False, "error": "Invalid role"}

        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_applications_{stamp}.csv"
        path = exports_dir / filename
        fieldnames = list(rows[0].keys()) if rows else ["application_id", "status", "applied_at"]
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        emailed = False
        if delivery in ("email", "both") and recipient:
            
            html = (
                f"<p>Your Katalyst applications export is ready</p>"
                f"<p>Rows: <strong>{len(rows)}</strong></p>"
                f"<p>The CSV is attached.</p>"
            )
            
            emailed = _send_email(
                subject="Katalyst: applications CSV export ready",
                html_body=html,
                to_addr=recipient,
                attachment_path=str(path),
                attachment_name=filename,
            )

        return {
            "ok": True,
            "filename": filename,
            "path": str(path),
            "row_count": len(rows),
            "delivery": delivery,
            "emailed": emailed,
        }
