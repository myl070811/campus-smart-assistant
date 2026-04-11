from flask import Flask

from .tasks import bp as tasks_bp
from .dashboard import bp as dashboard_bp
from .profile import bp as profile_bp
from .organizations import bp as organizations_bp
from .schedule import bp as schedule_bp
from .admin_awards import bp as admin_awards_bp
from .integrations import bp as integrations_bp
from .auth import bp as auth_bp


def register_routes(app: Flask) -> None:
    app.register_blueprint(tasks_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(organizations_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(admin_awards_bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(auth_bp)
