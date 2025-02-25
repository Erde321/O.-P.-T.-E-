import json
import queue
import threading
from flask import Flask, Response, stream_with_context, current_app
import time
import base64

clients = {
    "admin": [],
    "user": []
}

def notify_user(app, event_type):
    time.sleep(0.2)
    with app.app_context():
        from app import db
        from app.models import User, Project, Image, SelectedImage, ImageDetails
        """ Sendet eine Benachrichtigung an alle verbundenen User-SSE-Clients """
        message = {"event": event_type}

        if event_type == "update":
            open_project = Project.query.filter_by(status='offen').first()
            if open_project:
                message["open_project"] = {
                    "id": open_project.id,
                    "name": open_project.name,
                    "sync": open_project.sync
                }
                selected_image = db.session.query(Image).join(SelectedImage).filter(SelectedImage.project_id == open_project.id).first()
                if selected_image:
                    image_details = ImageDetails.query.filter_by(image_id=selected_image.id).first()
                    if image_details:
                        position_left, position_top = image_details.position.split(',')
                        message["largeImageSrc"] = f"data:image/{selected_image.extension};base64,{base64.b64encode(selected_image.data).decode('utf-8')}"
                        message["largeImageId"] = selected_image.id
                        message["position"] = {
                            "left": position_left,
                            "top": position_top
                        }
                        message["zoom"] = image_details.zoom
                    else:
                        message["largeImageSrc"] = None
                        message["largeImageId"] = None
                        message["position"] = None
                        message["zoom"] = None
                else:
                    message["largeImageSrc"] = None
                    message["largeImageId"] = None
                    message["position"] = None
                    message["zoom"] = None
            else:
                message["open_project"] = None
                message["largeImageSrc"] = None
                message["largeImageId"] = None
                message["position"] = None
                message["zoom"] = None

        message = json.dumps(message)
        for client in clients["user"]:
            try:
                client.put(message)
            except:
                pass  # Falls ein Client nicht mehr verbunden ist

def notify_admin(app, event_type):
    time.sleep(0.2)
    with app.app_context():
        from app import db
        from app.models import User, Project, Image, SelectedImage
        """ Sendet eine Benachrichtigung an alle verbundenen Admin-SSE-Clients """
        message = {"event": event_type}

        if event_type == "aktuelles_project_update":
            open_project = Project.query.filter_by(status='offen').first()
            if open_project:
                message["open_project"] = {
                    "id": open_project.id,
                    "name": open_project.name
                }
            else:
                message["open_project"] = None

        elif event_type == "user_update":
            users = User.query.all()
            message["users"] = [
                {
                    "id": user.id,
                    "username": user.name,
                    "is_online": user.online
                }
                for user in users
            ]

        elif event_type == "project_update":
            projects = Project.query.all()
            message["projects"] = [
                {
                    "id": project.id,
                    "name": project.name
                }
                for project in projects
            ]

        elif event_type == "card_update":
            open_project = Project.query.filter_by(status='offen').first()
            if open_project:
                images = Image.query.filter_by(project_id=open_project.id).all()
                message["open_project"] = {
                    "id": open_project.id,
                    "name": open_project.name
                }
                message["images"] = [
                    {
                        "id": image.id,
                        "name": image.filename,
                        "extension": image.extension,
                        "data": base64.b64encode(image.data).decode('utf-8')
                    }
                    for image in images
                ]
            else:
                message["open_project"] = None
                message["images"] = []

        elif event_type == "largeimageContainer_update":
            # Lade das aktuell ausgewählte Bild des aktuellen Projekts aus der Datenbank
            open_project = Project.query.filter_by(status='offen').first()
            if open_project:
                selected_image = db.session.query(Image).join(SelectedImage).filter(SelectedImage.project_id == open_project.id).first()
                if selected_image:
                    message["largeImageSrc"] = f"data:image/{selected_image.extension};base64,{base64.b64encode(selected_image.data).decode('utf-8')}"
                    message["largeImageId"] = selected_image.id
                    message["largeImageName"] = selected_image.filename
                    message["largeImageExtension"] = selected_image.extension
                    message["largeImageProjectId"] = selected_image.project_id
                else:
                    message["largeImageSrc"] = None
                    message["largeImageId"] = None
                    message["largeImageName"] = None
                    message["largeImageExtension"] = None
                    message["largeImageProjectId"] = None
            else:
                message["largeImageSrc"] = None
                message["largeImageId"] = None
                message["largeImageName"] = None
                message["largeImageExtension"] = None
                message["largeImageProjectId"] = None

        message = json.dumps(message)
        for client in clients["admin"]:
            try:
                client.put(message)
            except:
                pass  # Falls ein Client nicht mehr verbunden ist
