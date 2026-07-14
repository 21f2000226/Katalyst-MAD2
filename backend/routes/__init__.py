from backend.routes.admin_api import admin_bp
from backend.routes.company_api import company_bp
from backend.routes.auth import auth_bp
from backend.routes.public_api import public_bp
from backend.routes.health import health_bp
from backend.routes.student_api import student_bp
from backend.routes.jobs_api import jobs_bp


# Register required blue prints to the app

def register_blueprints(app):
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(jobs_bp)
