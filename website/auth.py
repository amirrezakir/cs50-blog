from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash , check_password_hash


auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        
        if user:

            if check_password_hash(user.password, password):
                flash("Logged in!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))

            else:
                flash("Password is incorrect.", category="erorr")

        else:   
              flash("Email does not exits.", category="erorr")    

    return render_template("login.html", user=current_user)

@auth.route("/sing-up", methods=['GET', 'POST'])
def singup():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists =  User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash("Email already in use.", category='erorr')

        elif username_exists:
            flash("This Username already exists.", category='erorr')

        elif password1 != password2:
            flash("password don\'t match!", category='erorr')

        elif len(username) < 2:
            flash("Username is too short!", category="erorr")

        elif len(password1) < 6:
            flash("Password is too short!", category='erorr')

        elif len(email) < 4:
            flash("Email is too short!", category='erorr')

        else:
            new_user = User(username=username, email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash("User created!")
            return redirect(url_for('views.home'))


    return render_template("singup.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))