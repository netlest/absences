from datetime import datetime
from flask import Blueprint, redirect, url_for, flash, request, render_template, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect as safe_redirect

from ..extensions import login_manager
from ..models import User

bp = Blueprint('auth', __name__)

    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/login')
def login():
    return render_template("auth/login.html")

@bp.route('/login', methods=['POST'])
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        
        # Set default values for the session if they are not already set
        session.setdefault("chunksize", 6)
        session.setdefault("start_month", datetime.today().month)
        session.setdefault("start_year", datetime.today().year)


        group_id = session.get("group_id")
        if not group_id:
            session["group_id"] = user.groups[0].id

        next = session.pop('next', None)
        return safe_redirect(next or url_for("main.index"))
    else:
        flash("Invalid username/password")
    
    return redirect(url_for("auth.login"))

@bp.route('/profile')
@login_required
def profile():
    return 'Logged in as: ' + current_user.username + ' UserID: ' + str(current_user.id)
 
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    next = session.pop('next', None)
    return safe_redirect(next or url_for("auth.login"))



