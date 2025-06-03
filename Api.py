from flask import Blueprint, jsonify
from flask_jwt_extended import  jwt_required, get_jwt_identity

import requests
from datetime import datetime
import pytz
from dateutil.parser import isoparse

from database import db, User 
from setup import cach

api_bp = Blueprint('api', __name__)



@api_bp.route("/api/user")
@jwt_required()
def get_user():
    #Hier muss noch überprüft werden ob es ein admin ist
    current_user = get_jwt_identity()
    user = db.session.query(User.username).all()
    return jsonify([u[0] for u in user])


@api_bp.route('/api/F1/drivers')
@cach.cached(timeout=7200)
def get_drivers():
    url = "http://api.jolpi.ca/ergast/f1/2025/drivers.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        fahrer = []
        data = response.json()
        drivers = data['MRData']['DriverTable']['Drivers']
        for d in drivers:
            name = f"{d['givenName']} {d['familyName']}"
            fahrer.append(name)
        return jsonify(fahrer)
    else:
        print("Fehler beim Abrufen der Daten: http://api.jolpi.ca/ergast/f1/2025/drivers.json")
    return None

@api_bp.route('/api/F1/races')
@cach.cached(timeout=7200)
def get_races():
    url = "http://api.jolpi.ca/ergast/f1/2025/races/"
    response = requests.get(url)
    
    if response.status_code == 200:
        races = []
        data = response.json()
        for r in data['MRData']['RaceTable']['Races']:
            races.append(f"{r['raceName']} / {r['date']}T{r['time']}")
        return races
    else:
        print("Fehler beim Abrufen der Daten http://api.jolpi.ca/ergast/f1/2025/races/")
        return None


@api_bp.route('/api/F1/next_race')
@cach.cached()
def get_next_race():
    all_races = get_races()
    for r in all_races:
        race_date = isoparse(r.split('/')[-1].strip())
        if race_date > datetime.now(tz=race_date.tzinfo):
            return jsonify(r.split('/')[0].strip())
    return None


@api_bp.route('/api/F1/next_race_time')
def get_next_race_time():
    all_races = get_races()
    for r in all_races:
        race_date = isoparse(r.split('/')[-1].strip())
        if race_date > datetime.now(tz=race_date.tzinfo):
            return jsonify(race_date.astimezone(pytz.timezone('Europe/Berlin')))
    return None