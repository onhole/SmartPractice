from flask import Blueprint, render_template, request, redirect, url_for
from .models import User, Note
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
            if email == '' or password == '':
                return render_template ("login.html", text="Put in actual stuff bro!!!")
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

        if email == '' or password == '' or name == '':
                return render_template ("signup.html")

        new_user = User(email=email, name=name, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)

        return redirect(url_for('views.home'))

    return render_template("signup.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/Note', methods=['GET', 'POST'])
def schedule():
    if request.method == 'POST':
        piece_artist = request.form.get('piece_artist')
        note = request.form.get('note')

        
    if request.method == 'GET':
        return render_template ("Note.html")

@auth.route('/delete', methods=['POST'])
@login_required
def delete():
    if request.method == 'POST':
        if 'delete' in request.form:
            deletednote = request.form.get('newnote') #string of the wanted deleted note
            wanttodelete = Note.query.filter_by(data=deletednote, user_id=current_user.id).first()

            db.session.delete(wanttodelete)
            db.session.commit()

    return redirect(url_for('views.home'))

