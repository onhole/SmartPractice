from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template ("index.html")

@auth.route('/logout')
def logout():
    return "logout"

@auth.route('/signout')
def signout():
    return "signout"

