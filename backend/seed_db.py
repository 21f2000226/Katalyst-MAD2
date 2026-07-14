"""
Database creation and population script for Katalyst V2.

can Run standalone from the backend/ folder:
  python seed_db.py
"""
import random

from faker import Faker
from flask_bcrypt import Bcrypt
from path_setup import ensure_project_root_on_path

ensure_project_root_on_path()

from backend import create_app
from backend.extensions import db
from backend.init_db import DEFAULT_ADMIN_PASSWORD, initialize_database
from backend.models import Application, Company, JobPosition, Placement, Student, User

Faker.seed(42)
random.seed(42)
fake = Faker("en_IN")
emails = [
    "@gmail.com",
    "@outlook.com",
    "@hotmail.com",
    "@ifheindia.org",
    ".iitm.ac.in",
    ".cbit.edu.net",
    ".mlrit.ac.in",
    "@pdgmbb.com",
    "@isb.edu.in",
]
company_emails = [
    "@kmpg.com",
    "@peopletech.com",
    "@googleindia.com",
    "@microsoft.com",
    "@workaday.com",
    "@teams.com",
]

STEM_SKILLS = [
    "Mathematics",
    "Statistics",
    "Chemical Engineering",
    "Computer Science",
    "Mechanical Engineering",
    "Electronics",
    "ECE",
    "Energy Systems",
    "Physics",
    "Data Structures",
    "Python",
    "Machine Learning",
    "Embedded Systems",
    "Control Systems",
    "Thermodynamics",
    "Circuit Design",
    "Signal Processing",
    "Python",
    "VLSI design",
    "Agentic AI",
    "RAG",
    "LLM's",
    "Java",
    "System Design",
    "DSA",
    "ML",
    "DL",
    "C++",
    "C",
    "Nvidia Jetson",
    "Rapids",
    "Data Science",
    "Neural Networks",
    "Backend",
]

STEM_JOBS = [
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Machine Learning Engineer",
    "Data Scientist",
    "AI Research Engineer",
    "Cybersecurity Analyst",
    "Cloud Engineer",
    "DevOps Engineer",
    "Mobile App Developer",
    "Embedded Systems Software Engineer",
    "Computer Vision Engineer",
    "Game Developer",
    "Blockchain Developer",
    "Mechanical Design Engineer",
    "Product Development Engineer",
    "Manufacturing Engineer",
    "Automotive Engineer",
    "Aerospace Engineer",
    "Thermal Engineer",
    "Robotics Engineer",
    "HVAC Engineer",
    "Energy Systems Engineer",
    "Materials Engineer",
    "Structural Analysis Engineer",
    "Quality Engineer",
    "Reliability Engineer",
    "Maintenance Engineer",
    "Mechatronics Engineer",
    "Electrical Engineer",
    "Power Systems Engineer",
    "Electronics Engineer",
    "Embedded Systems Engineer",
    "Control Systems Engineer",
    "Signal Processing Engineer",
    "RF Engineer",
    "VLSI Design Engineer",
    "Hardware Engineer",
    "FPGA Engineer",
    "ASIC Design Engineer",
    "Telecommunications Engineer",
    "Network Engineer",
    "Firmware Engineer",
    "Systems Engineer",
]

STEM_INDUSTRIES = [
    "IT",
    "Frontier AI",
    "Software & Services",
    "Semiconductors",
    "Aerospace",
    "Renewable Energy",
    "Robotics",
    "Electronics & Hardware",
    "Defence Tech",
    "Clean Tech",
    "Deep Tech",
    "Computer Vision",
    "Cloud & Infrastructure",
    "Med-Tech",
    "Bio-Tech",
    "Insurance",
    "Finance",
    "Quant",
    "Consulting",
]

NUM_COMPANIES = 6
NUM_STUDENTS = 40
DRIVES_PER_APPROVED_COMPANY = (2, 4)
APPLICATIONS_PER_STUDENT = (2, 6)
PLACEMENTS_COUNT = 8

app = create_app()


def seed_users_and_companies():
    bcrypt = Bcrypt(app)
    password_hash = bcrypt.generate_password_hash(DEFAULT_ADMIN_PASSWORD).decode("utf-8")
    companies = []
    used_emails = set()
    used_usernames = set()
    used_names = set()

    for i in range(NUM_COMPANIES):
        name = fake.company()[:120]
        while name in used_names:
            name = f"{fake.company()} {i}"[:120]
        used_names.add(name)

        # Build email once so the uniqueness check matches what we insert
        base = name.replace(",", "").replace(" ", "")
        email = f"hr_{base}_{i}{random.choice(company_emails)}".replace(" ", "_")[:120]
        while email in used_emails:
            email = f"hr_{base}_{i}_{random.randint(1000, 9999)}{random.choice(company_emails)}".replace(" ", "_")[:120]
        used_emails.add(email)

        username = f"co_{i}_{name.split()[0]}".replace(" ", "_").replace(",", "")[:80]
        while username in used_usernames:
            username = f"co_{i}_{fake.user_name()}"[:80]
        used_usernames.add(username)

        user = User(username=username, email=email, password_hash=password_hash, role="company")
        db.session.add(user)
        db.session.flush()

        approval = random.choice(["approved", "approved", "pending"])
        company = Company(
            user_id=user.id,
            name=name,
            website=fake.url(),
            hr_contact=fake.name(),
            industry=random.choice(STEM_INDUSTRIES),
            approval_status=approval,
        )
        db.session.add(company)
        companies.append(company)

    db.session.flush()
    print(f"Created {NUM_COMPANIES} company users and companies")
    return companies


def seed_students():
    bcrypt = Bcrypt(app)
    password_hash = bcrypt.generate_password_hash(DEFAULT_ADMIN_PASSWORD).decode("utf-8")
    students = []
    used_emails = set()

    for i in range(NUM_STUDENTS):
        first = fake.first_name()
        last = fake.last_name()
        full_name = f"{first} {last}"[:120]
        email = f"{first}.{last}{random.choice(emails)}"
        if email in used_emails:
            email = f"{first}.{last}{i}{random.choice(emails)}"
        used_emails.add(email)
        username = f"{first}_{last}".replace(" ", "_")[:80]

        user = User(username=username, email=email[:120], password_hash=password_hash, role="student")
        db.session.add(user)
        db.session.flush()
        student = Student(
            user_id=user.id,
            full_name=full_name,
            phone=fake.phone_number()[:20],
            resume_path=None,
            cgpa=round(random.uniform(6.0, 9.8), 2),
            graduation_year=random.randint(2024, 2026),
            skills=", ".join(random.sample(STEM_SKILLS, k=random.randint(2, 5))),
        )
        db.session.add(student)
        students.append(student)

    db.session.flush()
    print(f"Created {NUM_STUDENTS} student users and students")
    return students


def seed_job_positions(companies):
    approved = [company for company in companies if company.approval_status == "approved"]
    jobs = []

    for company in approved:
        count = random.randint(*DRIVES_PER_APPROVED_COMPANY)
        for _ in range(count):
            title = random.choice(STEM_JOBS)
            job = JobPosition(
                company_id=company.id,
                title=title,
                description=fake.paragraph(),
                requirements=",".join(random.choices(STEM_SKILLS, k=random.randint(3, 6))),
                # Structured cutoff so apply eligibility can be demoed (about 1 in 5 have none)
                min_cgpa=None if random.random() < 0.2 else round(random.uniform(6.0, 8.0), 1),
                salary_min=random.randint(3, 12) * 100000,
                salary_max=random.randint(12, 30) * 100000,
                deadline=fake.future_datetime(end_date="+30d"),
                status=random.choice(["active", "active", "closed"]),
                approval_status=random.choice(["approved", "approved", "pending"]),
            )
            db.session.add(job)
            jobs.append(job)

    db.session.flush()
    print(f"Created {len(jobs)} job positions (approved companies only)")
    return jobs


def seed_applications(students, jobs):
    approved_jobs = [job for job in jobs if job.approval_status == "approved"]
    if not approved_jobs:
        print("No approved job positions; skipping applications")
        return []

    applications = []
    seen = set()
    for student in students:
        count = random.randint(*APPLICATIONS_PER_STUDENT)
        chosen = random.sample(approved_jobs, min(count, len(approved_jobs)))
        for job in chosen:
            key = (student.id, job.id)
            if key in seen:
                continue
            # Respect CGPA cutoff when seeding (same rule as the apply API)
            if job.min_cgpa is not None and (student.cgpa is None or student.cgpa < job.min_cgpa):
                continue
            seen.add(key)
            application = Application(
                student_id=student.id,
                job_position_id=job.id,
                status=random.choice(["applied", "applied", "shortlisted", "selected", "rejected"]),
            )
            db.session.add(application)
            applications.append(application)

    db.session.flush()
    print(f"Created {len(applications)} applications (no duplicates)")
    return applications


def seed_placements(applications):
    selected = [application for application in applications if application.status == "selected"]
    to_place = selected[:PLACEMENTS_COUNT]
    for application in to_place:
        db.session.add(
            Placement(
                application_id=application.id,
                student_id=application.student_id,
                company_id=application.job_position.company_id,
                salary=round(random.uniform(6.0, 24.0), 2),
                joining_date=fake.future_date(end_date="+90d"),
            )
        )
    db.session.flush()
    print(f"Created {len(to_place)} placements.")


def run():
    with app.app_context():
        db.drop_all()
        db.create_all()
        initialize_database()
        companies = seed_users_and_companies()
        students = seed_students()
        jobs = seed_job_positions(companies)
        applications = seed_applications(students, jobs)
        seed_placements(applications)
        db.session.commit()
        print("Database population complete.")


if __name__ == "__main__":
    run()
