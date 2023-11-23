from flask import Blueprint, render_template, request

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form
    print(data)
    return render_template ("login.html", text="Balls")

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
    return render_template ("signup.html")

@auth.route('/logout')
def logout():
    return "logout"

@auth.route('/schedule')
def schedule():
    return render_template ("schedule.html")

