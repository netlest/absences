import os
from datetime import datetime, date
from flask import Response, Blueprint, flash, redirect, render_template, session, url_for, current_app, send_from_directory
from flask_login import login_required, current_user
from ..image import AbsMonth
from ..forms import NavForm, PrevNextForm

def generate_dates(start_month, start_year, N):
    dates = []
    current_date = datetime(start_year, start_month, 1)
    
    for _ in range(N):
        dates.append(current_date)
        next_month = current_date.month % 12 + 1
        next_year = current_date.year + (current_date.month // 12)
        current_date = datetime(next_year, next_month, 1)
    
    return dates

def add_months(givendate, months):
    # Calculate the target month and year
    total_months = givendate.month - 1 + months
    new_year = givendate.year + total_months // 12
    new_month = total_months % 12 + 1
    # Handle cases where the new day exceeds the last day of the new month
    # Safely calculate the last day of the target month
    if new_month == 12:  # December, next month is January of next year
        next_month_start = date(new_year + 1, 1, 1)
    else:
        next_month_start = date(new_year, new_month + 1, 1)
    last_day_of_new_month = (next_month_start - date(new_year, new_month, 1)).days
    new_day = min(givendate.day, last_day_of_new_month)
    return date(new_year, new_month, new_day)

bp = Blueprint("main", __name__)

@bp.route("/")
@login_required
def index():
    chunksize = session.get("chunksize", 4)
    start_month = session.get("start_month", datetime.today().month)
    start_year = session.get("start_year", datetime.today().year)

    navform = NavForm()
    prevnextform = PrevNextForm()

    dates = generate_dates(start_month, start_year, chunksize)
    img_maps = []
    for date in dates:
        year = date.year
        month = date.month
        img_map = AbsMonth(current_app.config, year, month).img_map
        img_maps.append(img_map)

    return render_template("main/index.html", img_maps=img_maps, dates=dates, navform=navform, prevnextform=prevnextform)

@bp.route("/submit", methods=["POST"])
@login_required
def submit():
    navform = NavForm()
    if navform.validate_on_submit():
        session['group_id'] = navform.group_id.data
        session["chunksize"] = navform.chunksize.data
        session["start_month"] = navform.start_month.data
        session["start_year"] = navform.start_year.data
        current_app.logger.info(f"{navform.chunksize.data=}, {navform.start_month.data=}, {navform.start_year.data=}")
    else:
        flash(f"Input invalid: {navform.errors}")
        current_app.logger.info(f"Input invalid {navform.errors}")

    return redirect(url_for("main.index"))

@bp.route("/prev", methods=["POST"])
@login_required
def navigation():
    prevnextform = PrevNextForm()
    if prevnextform.validate_on_submit():

        chunksize = session.get("chunksize", 4)
        start_month = session.get("start_month", datetime.today().month)
        start_year = session.get("start_year", datetime.today().year)

        givendate = date(start_year, start_month, 1)
        prevdate = add_months(givendate, -chunksize)
        nextdate = add_months(givendate, chunksize)

        if prevnextform.prev.data:
            session["start_month"] = prevdate.month
            session["start_year"] = prevdate.year
        elif prevnextform.next.data:
            session["start_month"] = nextdate.month
            session["start_year"] = nextdate.year
    else:
        current_app.logger.info(f"Input invalid {prevnextform.errors}")

    return redirect(url_for("main.index"))


@bp.route("/favicon.ico")
def favicon() -> Response:
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico", mimetype="image/vnd.microsoft.icon",
    )
