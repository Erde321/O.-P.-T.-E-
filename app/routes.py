from flask import Blueprint, render_template, request, redirect, url_for, session, Response, stream_with_context, current_app, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User, Project, Image, SelectedImage, ImageDetails, Admin, ActiveSession, db
from app.sse import notify_admin, notify_user
from datetime import datetime, timedelta
import base64
import threading
import time
import queue
from app.sse import clients

main = Blueprint('main', __name__)

@main.route('/sse/admin')
def sse_admin():
    """ Endpunkt für Server-Sent Events (SSE) """
    def event_stream_admin():
        client_queue = queue.Queue()
        clients["admin"].append(client_queue)
        try:
            while True:
                msg = client_queue.get()
                yield f"data: {msg}\n\n"
        except GeneratorExit:
            clients["admin"].remove(client_queue)  # Verbindung beenden

    return Response(stream_with_context(event_stream_admin()), content_type='text/event-stream')

@main.route('/sse/user')
def sse_user():
    """ Endpunkt für Server-Sent Events (SSE) """
    def event_stream_user():
        client_queue = queue.Queue()
        clients["user"].append(client_queue)
        try:
            while True:
                msg = client_queue.get()
                yield f"data: {msg}\n\n"
        except GeneratorExit:
            clients["user"].remove(client_queue)  # Verbindung beenden

    return Response(stream_with_context(event_stream_user()), content_type='text/event-stream')

@main.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        if 'user_login' in request.form:
            username = request.form['username']
            user = User.query.filter_by(name=username).first()
            if user:
                session['user_id'] = user.id
                user.online = True
                user.last_active = datetime.utcnow()
                db.session.commit()
                # Sitzung aktualisieren oder erstellen
                active_session = ActiveSession.query.filter_by(user_id=user.id).first()
                if (active_session):
                    active_session.last_active = datetime.utcnow()
                else:
                    new_session = ActiveSession(user_id=user.id, last_active=datetime.utcnow())
                    db.session.add(new_session)
                db.session.commit()
                return redirect(url_for('main.user_dashboard'))
            else:
                new_user = User(name=username, password=generate_password_hash('password'))
                db.session.add(new_user)
                db.session.commit()
                session['user_id'] = new_user.id
                # Sitzung erstellen
                new_session = ActiveSession(user_id=new_user.id, last_active=datetime.utcnow())
                db.session.add(new_session)
                db.session.commit()
                return redirect(url_for('main.user_dashboard'))
        elif 'admin_login' in request.form:
            admin_password = request.form['admin_password']
            admin = Admin.query.first()
            if admin:
                if check_password_hash(admin.password, admin_password):
                    session['admin_id'] = admin.id
                    admin.last_active = datetime.utcnow()
                    db.session.commit()
                    return redirect(url_for('main.admin_dashboard'))
                else:
                    error = "Falsches Passwort!"
            else:
                new_admin = Admin(password=generate_password_hash(admin_password))
                db.session.add(new_admin)
                db.session.commit()
                session['admin_id'] = new_admin.id
                return redirect(url_for('main.admin_dashboard'))
    return render_template('index.html', error=error)

@main.route('/admin_dashboard')
def admin_dashboard():
    # Setze alle Projekte auf "geschlossen", außer das Projekt "geschlossen"
        
    current_project = Project.query.filter_by(status='offen').first()
    large_image_src = None

    if current_project:
        selected_image = db.session.query(Image).join(SelectedImage).filter(SelectedImage.project_id == current_project.id).first()
        if selected_image:
            large_image_src = f"data:image/{selected_image.extension};base64,{base64.b64encode(selected_image.data).decode('utf-8')}"

    # Benachrichtige die SSE-Clients über die Aktualisierung in einem separaten Thread mit Verzögerung
    threading.Thread(target=notify_admin, args=(current_app._get_current_object(), "aktuelles_project_update"), daemon=True).start()
    threading.Thread(target=notify_admin, args=(current_app._get_current_object(), "project_update"), daemon=True).start()
    threading.Thread(target=notify_admin, args=(current_app._get_current_object(), "card_update"), daemon=True).start()
    threading.Thread(target=notify_admin, args=(current_app._get_current_object(), "user_update"), daemon=True).start()
    threading.Thread(target=notify_admin, args=(current_app._get_current_object(), "largeimageContainer_update"), daemon=True).start()
    
    return render_template('admin_dashboard.html', current_project=current_project, large_image_src=large_image_src)

@main.route('/user_dashboard')
def user_dashboard():
    # Benachrichtige die SSE-Clients über die Aktualisierung
    threading.Thread(target=notify_user, args=(current_app._get_current_object(), 'update'), daemon=True).start()
    return render_template('user_dashboard.html')

@main.route('/get_current_project_image', methods=['GET'])
def get_current_project_image():
    current_project = Project.query.filter_by(status='offen').first()
    if current_project:
        selected_image = db.session.query(Image).join(SelectedImage).filter(SelectedImage.project_id == current_project.id).first()
        if selected_image:
            return jsonify({
                "largeImageSrc": f"data:image/{selected_image.extension};base64,{base64.b64encode(selected_image.data).decode('utf-8')}",
                "largeImageId": selected_image.id,
                "largeImageName": selected_image.filename,
                "largeImageExtension": selected_image.extension
            })
    return jsonify({
        "largeImageSrc": None,
        "largeImageId": None,
        "largeImageName": None,
        "largeImageExtension": None
    })

@main.route('/open_project', methods=['POST'])
def open_project():
    project_id = request.form.get('project_id')
    if project_id:
        # Schließe das aktuell geöffnete Projekt
        current_project = Project.query.filter_by(status='offen').first()
        if current_project:
            current_project.status = 'geschlossen'
            db.session.commit()

        # Öffne das ausgewählte Projekt
        new_project = Project.query.get(project_id)
        if new_project:
            new_project.status = 'offen'
            db.session.commit()

            # Benachrichtige die SSE-Clients über die Aktualisierung
            notify_admin(current_app._get_current_object(), 'project_update')
            notify_admin(current_app._get_current_object(), 'aktuelles_project_update')
            notify_admin(current_app._get_current_object(), 'card_update')
            notify_admin(current_app._get_current_object(), 'user_update')
            notify_admin(current_app._get_current_object(), 'largeimageContainer_update')
            notify_user(current_app._get_current_object(), 'update')
            
    return '', 204

@main.route('/create_project', methods=['POST'])
def create_project():
    project_name = request.form.get('project_name')
    if project_name:
        new_project = Project(name=project_name, status='geschlossen')
        db.session.add(new_project)
        db.session.commit()
        # Benachrichtige die SSE-Clients über die Aktualisierung
        notify_admin(current_app._get_current_object(), 'project_update')
        notify_admin(current_app._get_current_object(), 'aktuelles_project_update')
        notify_admin(current_app._get_current_object(), 'card_update')
        notify_admin(current_app._get_current_object(), 'user_update')
        notify_admin(current_app._get_current_object(), 'largeimageContainer_update')
        
    return '', 204

@main.route('/delete_project', methods=['POST'])
def delete_project():
    project_id = request.form.get('project_id')
    project = Project.query.get(project_id)
    if project:
        # Lösche alle Bilder, die zu diesem Projekt gehören
        images = Image.query.filter_by(project_id=project_id).all()
        for image in images:
            # Lösche die zugehörigen ImageDetails
            image_details = ImageDetails.query.filter_by(image_id=image.id).first()
            if image_details:
                db.session.delete(image_details)
            db.session.delete(image)
        
        db.session.delete(project)
        db.session.commit()
        
        # Benachrichtige die SSE-Clients über die Aktualisierung
        notify_admin(current_app._get_current_object(), 'project_update')
        notify_admin(current_app._get_current_object(), 'aktuelles_project_update')
        notify_admin(current_app._get_current_object(), 'card_update')
        notify_admin(current_app._get_current_object(), 'user_update')
        notify_admin(current_app._get_current_object(), 'largeimageContainer_update')
        notify_user(current_app._get_current_object(), 'update')
    return '', 204

@main.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        # Benachrichtige die SSE-Clients über die Aktualisierung
        notify_admin(current_app._get_current_object(), 'project_update')
        notify_admin(current_app._get_current_object(), 'aktuelles_project_update')
        notify_admin(current_app._get_current_object(), 'card_update')
        notify_admin(current_app._get_current_object(), 'user_update')
        notify_admin(current_app._get_current_object(), 'largeimageContainer_update')
    return '', 204

@main.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' in request.files:
        file = request.files['file']

        if file.filename != '':
            project_id = request.form.get('project_id')

            if project_id:
                project = Project.query.get(project_id)
                
                if project:
                    # Lese die Datei als Bytes
                    file_data = file.read()
                    
                    # Erstelle ein neues Bild in der Datenbank
                    new_image = Image(
                        project_id=project.id,
                        filename=file.filename,
                        data=file_data,
                        extension=file.filename.split('.')[-1]
                    )
                    db.session.add(new_image)
                    db.session.commit()
                    
                    # Benachrichtige die SSE-Clients über die Aktualisierung
                    notify_admin(current_app._get_current_object(), 'project_update')
                    notify_admin(current_app._get_current_object(), 'aktuelles_project_update')
                    notify_admin(current_app._get_current_object(), 'card_update')
                    notify_admin(current_app._get_current_object(), 'user_update')
                    notify_admin(current_app._get_current_object(), 'largeimageContainer_update')
    return '', 204

@main.route('/update_image_name', methods=['POST'])
def update_image_name():
    image_id = request.form.get('image_id')
    new_name = request.form.get('new_name')
    
    if image_id and new_name:
        image = Image.query.get(image_id)
        if image:
            image.filename = new_name
            db.session.commit()
            # Benachrichtige die SSE-Clients über die Aktualisierung
            notify_admin(current_app._get_current_object(), 'project_update')
            notify_admin(current_app._get_current_object(), 'aktuelles_project_update')
            notify_admin(current_app._get_current_object(), 'card_update')
            notify_admin(current_app._get_current_object(), 'user_update')
            notify_admin(current_app._get_current_object(), 'largeimageContainer_update')
    return '', 204

@main.route('/delete_image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    image = Image.query.get(image_id)
    if image:
        # Lösche den Eintrag in ImageDetails
        image_details = ImageDetails.query.filter_by(image_id=image_id).first()
        if image_details:
            db.session.delete(image_details)
        
        db.session.delete(image)
        db.session.commit()
        
        # Benachrichtige die SSE-Clients über die Aktualisierung
        notify_admin(current_app._get_current_object(), 'project_update')
        notify_admin(current_app._get_current_object(), 'aktuelles_project_update')
        notify_admin(current_app._get_current_object(), 'card_update')
        notify_admin(current_app._get_current_object(), 'user_update')
        notify_admin(current_app._get_current_object(), 'largeimageContainer_update')
        notify_user(current_app._get_current_object(), 'update')
    return '', 204

@main.route('/update_sync', methods=['POST'])
def update_sync():
    sync = request.form.get('sync') == 'on'
    current_project = Project.query.filter_by(status='offen').first()
    if current_project:
        current_project.sync = sync
        db.session.commit()
        notify_user(current_app._get_current_object(), 'update')
    return '', 204

@main.route('/update_user_session', methods=['POST'])
def update_user_session():
    user_id = request.form.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            active_session = ActiveSession.query.filter_by(user_id=user_id).first()
            if active_session:
                active_session.last_active = datetime.utcnow()
            else:
                new_session = ActiveSession(user_id=user_id, last_active=datetime.utcnow())
                db.session.add(new_session)
            db.session.commit()
    return '', 204

@main.route('/logout')
def logout():
    # Überprüfe, ob der Admin sich ausloggt
    if 'admin_id' in session:
        admin_id = session.pop('admin_id', None)
        if admin_id:
            admin = Admin.query.get(admin_id)
            if admin:
                admin.last_active = datetime.utcnow()
                db.session.commit()
        
        # Schließe alle Projekte außer "geschlossen"
        projects = Project.query.filter(Project.name != 'geschlossen').all()
        for project in projects:
            project.status = 'geschlossen'
        
        # Setze das Projekt "geschlossen" auf offen
        closed_project = Project.query.filter_by(name='geschlossen').first()
        if closed_project:
            closed_project.status = 'offen'
        
        db.session.commit()
        
    
    # Lösche die Sitzung des Benutzers, falls vorhanden
    user_id = session.pop('user_id', None)
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.online = False
            db.session.commit()
            # Benachrichtige die SSE-Clients über die Aktualisierung
            notify_admin(current_app._get_current_object(), 'user_update')
    
    return redirect(url_for('main.index'))

@main.route('/update_admin_session', methods=['POST'])
def update_admin_session():
    admin_id = session.get('admin_id')
    if admin_id:
        admin = Admin.query.get(admin_id)
        if admin:
            admin.last_active = datetime.utcnow()
            db.session.commit()
    return '', 204

@main.route('/update_image_details', methods=['POST'])
def update_image_details():
    data = request.get_json()
    image_id = data.get('image_id')
    position = data.get('position')
    zoom = data.get('zoom')

    if image_id and position and zoom:
        image_details = ImageDetails.query.filter_by(image_id=image_id).first()
        if image_details:
            image_details.position = f"{position['left']},{position['top']}"
            image_details.zoom = float(zoom.replace('scale(', '').replace(')', ''))
        else:
            new_image_details = ImageDetails(
                image_id=image_id,
                position=f"{position['left']},{position['top']}",
                zoom=float(zoom.replace('scale(', '').replace(')', ''))
            )
            db.session.add(new_image_details)
        db.session.commit()
        notify_user(current_app._get_current_object(), 'update')
    return '', 204

@main.route('/get_project_status', methods=['GET'])
def get_project_status():
    current_project = Project.query.filter_by(status='offen').first()
    if current_project and current_project.name != 'geschlossen':
        selected_image = db.session.query(Image).join(SelectedImage).filter(SelectedImage.image_id == Image.id).first()
        large_image_src = f"data:image/{selected_image.extension};base64,{selected_image.data.decode('utf-8')}" if selected_image else ''
    return '', 204

@main.route('/select_image', methods=['POST'])
def select_image():
    data = request.get_json()
    image_id = data.get('image_id')
    project_id = data.get('project_id')

    if image_id and project_id:
        # Entferne die aktuelle Auswahl
        SelectedImage.query.filter_by(project_id=project_id).delete()

        # Füge die neue Auswahl hinzu
        selected_image = SelectedImage(project_id=project_id, image_id=image_id)
        db.session.add(selected_image)
        db.session.commit()

        # Benachrichtige die SSE-Clients über die Aktualisierung
        notify_admin(current_app._get_current_object(), 'largeimageContainer_update')
        notify_user(current_app._get_current_object(), 'update')

    return '', 204


