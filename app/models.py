from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)  # Passwortfeld hinzugefügt
    online = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)  # last_active hinzugefügt

class ActiveSession(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    status = db.Column(db.String(50), default='geschlossen')
    sync = db.Column(db.Boolean, default=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(150), nullable=False)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)  # last_active hinzugefügt

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    filename = db.Column(db.String(150), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    extension = db.Column(db.String(10), nullable=False)

class ImageDetails(db.Model):
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), primary_key=True)
    position = db.Column(db.String(150), nullable=True)
    zoom = db.Column(db.Float, nullable=True)

class SelectedImage(db.Model):
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)