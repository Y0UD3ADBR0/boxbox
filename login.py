from flask import Blueprint, redirect, render_template, request
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from security import verify_password, hash_password

from database import User, db

login_bp = Blueprint('login', __name__)





@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        usr = User.query.filter_by(username=username).first()

        if verify_password(password, usr.password_hash):
            access_token = create_access_token(identity=usr.username, additional_claims={"id": usr.id})
            response = redirect("/")
            set_access_cookies(response, access_token)
            return response
        
        else:
            return "404"

    return render_template("Login.html")
    


@login_bp.route("/logout", methods=["POST"])
def logout():
    return unset_jwt_cookies(redirect("/"))


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_verify = request.form['password_verify']
        if password == password_verify:
            password = hash_password(password)
            new_user = User(username=username,password_hash=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template("Login.html")
    return render_template("Register.html")
