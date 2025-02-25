import os

class Config:
    SECRET_KEY = 'GeheimerSchluessel'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'datenbank.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False