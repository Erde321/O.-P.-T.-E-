from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import time
from .sse import notify_admin, notify_user
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        from .routes import main
        app.register_blueprint(main)  # Registriere die Routen
    
    return app

def check_user_sessions(app):
    from .models import User, ActiveSession
    while True:
        with app.app_context():
            expired_sessions = ActiveSession.query.filter(
                ActiveSession.last_active < datetime.utcnow() - timedelta(seconds=3)
            ).all()
            for session in expired_sessions:
                user = User.query.get(session.user_id)
                if user:
                    user.online = False
                    db.session.delete(session)
                    db.session.commit()
                    notify_admin(app, "user_update")
        time.sleep(3)  # Überprüfe alle 3 Sekunden

def check_admin_session(app):
    from .models import Admin, Project
    while True:
        with app.app_context():
            expired_sessions = Admin.query.filter(
                Admin.last_active < datetime.utcnow() - timedelta(seconds=3)
            ).all()
            if expired_sessions:
                # Schließe alle Projekte außer "geschlossen"
                Project.query.filter(Project.name != 'geschlossen').update({'status': 'geschlossen'})
                # Setze das Projekt "geschlossen" auf offen
                Project.query.filter_by(name='geschlossen').update({'status': 'offen'})
                db.session.commit()
                notify_user(app, "update")
        time.sleep(3)  # Überprüfe alle 3 Sekunden

def default_db(app):
    from .models import User, Project
    with app.app_context():
        # Alle Benutzer auf offline setzen
        User.query.update({'online': False})

        # Projekt "geschlossen" erstellen, falls es nicht existiert, und öffnen
        if not Project.query.filter_by(name='geschlossen').first():
            closed_project = Project(name='geschlossen', status='geschlossen')
            db.session.add(closed_project)
        else:
            closed_project = Project.query.filter_by(name='geschlossen').first()
            closed_project.status = 'offen'
        db.session.commit()