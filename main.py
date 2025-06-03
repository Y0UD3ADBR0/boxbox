import datetime
from flask import Flask, jsonify, redirect, render_template, request
from flask_caching import Cache



from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies, jwt_required, get_jwt_identity, unset_jwt_cookies
import requests
from datetime import datetime
from dateutil.parser import isoparse
import json

from database import db, User, Race, Bets
import security
import pytz


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
jwt = JWTManager(app)



@jwt.unauthorized_loader
def redirect_to_login(callback):
    return redirect('/login')


@app.route('/')
def index():
    return render_template("Home.html")

@app.route("/F1")
@jwt_required()
def f1():
    return render_template("Wetten.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        usr = User.query.filter_by(username=username).first()

        if security.verify_password(password, usr.password_hash):
            access_token = create_access_token(identity=usr.username, additional_claims={"id": usr.id})
            response = redirect("/")
            set_access_cookies(response, access_token)
            return response
        
        else:
            return "404"

    return render_template("Login.html")

@app.route("/logout", methods=["POST"])
def logout():
    return unset_jwt_cookies(redirect("/"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_verify = request.form['password_verify']
        if password == password_verify:
            password = security.hash_password(password)
            new_user = User(username=username,password_hash=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template("Login.html")
    return render_template("Register.html")


@app.route('/api/F1/drivers')
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
        print(f"Fehler beim Abrufen der Daten: {response.status_code}")
    return None

@app.route('/api/F1/races')
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


@app.route('/api/F1/next_race')
@cach.cached()
def get_next_race():
    all_races = get_races()
    for r in all_races:
        race_date = isoparse(r.split('/')[-1].strip())
        if race_date > datetime.now(tz=race_date.tzinfo):
            return jsonify(r.split('/')[0].strip())
    return None


@app.route('/api/F1/next_race_time')
def get_next_race_time():
    all_races = get_races()
    for r in all_races:
        race_date = isoparse(r.split('/')[-1].strip())
        if race_date > datetime.now(tz=race_date.tzinfo):
            return jsonify(race_date.astimezone(pytz.timezone('Europe/Berlin')))
    return None

if __name__ == '__main__':

    app.run(debug=True)
