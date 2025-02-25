from app import create_app, default_db, check_user_sessions, check_admin_session
import threading
import os
from app import db

app = create_app()

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    default_db(app)  # setzt dynamische Werte zurück

    # Starte den Hintergrundthread um zu prüfen wer online ist
    threading.Thread(target=check_user_sessions, args=(app,), daemon=True).start()

    # Starte den Hintergrundthread um zu prüfen wer online ist
    threading.Thread(target=check_admin_session, args=(app,), daemon=True).start()

    app.run(debug=True, use_reloader=False)