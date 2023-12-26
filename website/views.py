from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from . import db
from .models import Note, User


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        thenote = request.form.get('note')

        newnote = Note(data=thenote, user_id=current_user.id)
        db.session.add(newnote)
        db.session.commit()

    return render_template ('home.html', user=current_user)

