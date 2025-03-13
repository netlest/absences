from urllib.parse import urlparse
from flask import  Blueprint, current_app, request, render_template, make_response, url_for, flash, redirect
from ..forms import NavForm, PrevNextForm
from flask_login import login_required, current_user

bp = Blueprint("sitemap", __name__)

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

@bp.route("/sitemap")
@bp.route("/sitemap/")
@bp.route("/sitemap.xml")
@login_required
def sitemap():
    static_urls = get_static_urls()
    xml_sitemap = render_template("sitemap/sitemap.xml", static_urls=static_urls)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"
    return response
