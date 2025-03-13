from urllib.parse import urlparse
from flask import  Blueprint, current_app, request, render_template, make_response, url_for, flash, redirect
from ..forms import NavForm, PrevNextForm
from flask_login import login_required, current_user

bp = Blueprint("manage", __name__)


@bp.route("/manage")
@login_required
def manage():
    navform = NavForm()
    prevnextform = PrevNextForm()
    return render_template("manage/index.html",  navform=navform, prevnextform=prevnextform)

