

from flask import redirect, render_template
from flask_jwt_extended import jwt_required

from login import login_bp
from Api import api_bp
from setup import app, jwt 

app.register_blueprint(login_bp)
app.register_blueprint(api_bp)

@jwt.unauthorized_loader
def redirect_to_login():
    return redirect('/login')

@app.route('/')
def index():
    return render_template("Home.html")

@app.route("/F1")
@jwt_required()
def f1():
    return render_template("Wetten.html")



if __name__ == '__main__':

    app.run(debug=True)
