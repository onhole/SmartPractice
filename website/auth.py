from flask import Blueprint, current_app, render_template, request, redirect, url_for
import os
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from .models import User, Note, Piece
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from . import create_app
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)
class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

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
@login_required
def schedule():
    form = UploadFileForm()
    if form.validate_on_submit():
        uploaded_file = form.file.data  # Get the file object from the form
        
        if uploaded_file and hasattr(uploaded_file, 'filename'):
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, secure_filename(uploaded_file.filename))
            
            uploaded_file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), file_path))
            # Save the uploaded file to the desired location
            
            # Rest of your code...
    if request.method == 'POST':
        piece_artist = request.form.get('piece_artist')
        note = request.form.get('note')

        new_piece = Piece(title=piece_artist, note=note, user_id=current_user.id)
        db.session.add(new_piece)
        db.session.commit()

    return render_template ("Note.html", user=current_user, form=form)

@auth.route('delete_piece', methods=["POST"])
@login_required
def delete_piece():
    deleted_piece_id = request.form.get('piece_id')

    if deleted_piece_id:
        piecedeleted = Piece.query.get(deleted_piece_id)

        if piecedeleted:
            db.session.delete(piecedeleted)
            db.session.commit()

    return redirect(url_for('auth.schedule'))

@auth.route('/edit_piece', methods=["POST"])
@login_required
def edit_piece():
    editpieceid = request.form.get('piece_id')
    pieceedited = Piece.query.get(editpieceid)

    db.session.delete(pieceedited)
    db.session.commit()

    return redirect(url_for('auth.schedule'))

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

