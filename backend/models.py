
from datetime import datetime

from backend.extensions import db

# SQLAlchemy data models for the placement portal.
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # admin / student / company / blacklisted
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    company = db.relationship("Company", back_populates="user", uselist=False)
    student = db.relationship("Student", back_populates="user", uselist=False)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    resume_path = db.Column(db.String(255))
    cgpa = db.Column(db.Float)
    graduation_year = db.Column(db.Integer)
    skills = db.Column(db.Text)
    # if False, daily deadline emails skip this student
    notify_deadlines = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="student")
    applications = db.relationship("Application", back_populates="student", cascade="all, delete-orphan")
    placements = db.relationship("Placement", back_populates="student", cascade="all, delete-orphan")


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(120))
    industry = db.Column(db.String(100))
    approval_status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="company")
    job_positions = db.relationship("JobPosition", back_populates="company", cascade="all, delete-orphan")
    placements = db.relationship("Placement", back_populates="company", cascade="all, delete-orphan")


class JobPosition(db.Model):
    # UI calls these "drives". Table is job_positions (old V1 name was drives).
    __tablename__ = "job_positions"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    # NULL = no CGPA cutoff
    min_cgpa = db.Column(db.Float, nullable=True)
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="active", nullable=False)
    approval_status = db.Column(db.String(20), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    company = db.relationship("Company", back_populates="job_positions")
    applications = db.relationship("Application", back_populates="job_position", cascade="all, delete-orphan")


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    job_position_id = db.Column(db.Integer, db.ForeignKey("job_positions.id"), nullable=False)
    status = db.Column(db.String(20), default="applied", nullable=False)
    # filled in when company shortlists
    interview_at = db.Column(db.DateTime, nullable=True)
    interview_notes = db.Column(db.String(255), nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = db.relationship("Student", back_populates="applications")
    job_position = db.relationship("JobPosition", back_populates="applications")
    placement = db.relationship("Placement", back_populates="application", uselist=False)

    __table_args__ = (
        db.UniqueConstraint("student_id", "job_position_id", name="uq_student_job_position"),
    )


class Placement(db.Model):
    # created when company selects a student. salary is required. 
    __tablename__ = "placements"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    joining_date = db.Column(db.Date, nullable=True)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    application = db.relationship("Application", back_populates="placement")
    student = db.relationship("Student", back_populates="placements")
    company = db.relationship("Company", back_populates="placements")
