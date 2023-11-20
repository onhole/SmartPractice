from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "yasss"

@auth.route('/logout')
def logout():
    return "logout"

@auth.route('/signout')
def signout():
    return "signout"

