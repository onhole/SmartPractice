from flask import Blueprint, render_template, request, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        check = User.query.filter_by(email=email).first()
        if check:
            if check_password_hash(check.password, password):
                login_user(check, remember=True)
                return redirect(url_for('views.home'))
            else:
                return render_template ("login.html", text="Wrong info bro !!!")
    return render_template ("login.html", text="Welcome back!  We're glad your back.")

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        new_user = User(email=email, name=name, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)

        return redirect(url_for('views.home'))

    return render_template ("signup.html")

@auth.route('/logout')
@login_required
def logout():
    return redirect(url_for('auth.login'))

@auth.route('/schedule')
def schedule():
    return render_template ("schedule.html")

