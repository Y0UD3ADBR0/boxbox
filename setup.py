
from flask import Flask
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from datetime import timedelta
from database import db
import json


app = Flask(__name__)

cach = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 60
})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)
with app.app_context():
    db.create_all()


with open("config.json","r") as f:
    config_data = json.load(f)
    
app.config['JWT_SECRET_KEY'] = config_data["JWT_SECRET_KEY"]
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # True bei HTTPS
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Optional für einfache Nutzung umstellen fals sicherheit benötigt wird
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)