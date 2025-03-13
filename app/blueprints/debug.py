from urllib.parse import urlparse
from flask import  Blueprint, current_app, request, render_template, url_for, flash, session, redirect
from ..forms import NavForm, PrevNextForm
from flask_login import login_required, current_user
from ..extensions import db

bp = Blueprint("debug", __name__)

@bp.before_request
@login_required
def restrict_to_admins():
    if  not current_user.admin:
        flash('You do not have permission to view this page', 'error')
        return redirect(url_for('main.index'))

def get_static_urls():
    host_components = urlparse(request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc
    static_urls = list()

    for rule in current_app.url_map.iter_rules():
        if not str(rule).startswith("/admin"):
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url = {
                    "loc": f"{host_base}{str(rule)}"
                }
                static_urls.append(url)

    return static_urls

@bp.route("/debug")
@login_required
def index():
    navform = NavForm()
    prevnextform = PrevNextForm()
    static_urls = get_static_urls()

    engine = db.get_engine()
    dialect = engine.dialect.name

    # I want to display all flask session content

    session_content = session
    current_app.logger.info(f"Session content: {session_content}")

    return render_template("debug/index.html", dialect=dialect, static_urls=static_urls, navform=navform, prevnextform=prevnextform)

