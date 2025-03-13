from flask import Blueprint, current_app, request, render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
from ..forms import HolidayForm, NavForm, PrevNextForm
from ..models import Holiday

bp = Blueprint("holiday", __name__)

@bp.before_request
@login_required
def restrict_to_admins():
    if  not current_user.admin:
        flash('You do not have permission to view this page', 'error')
        return redirect(url_for('main.index'))

@bp.route("/holidays")
@login_required
def index():
    navform = NavForm()
    prevnextform = PrevNextForm()
    holidays = db.session.query(Holiday).all()
    return render_template(
        "holiday/index.html", 
        holidays=holidays, 
        navform=navform, 
        prevnextform=prevnextform
    )

@bp.route("/holidays/create", methods=["GET"])
@login_required
def create():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = HolidayForm()

    return render_template(
        'holiday/create.html',
        form=form, 
        navform=navform, prevnextform=prevnextform,
        action_url=url_for('holiday.create_post')
    )

@bp.route("/holidays/create", methods=["POST"])
@login_required
def create_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = HolidayForm()

    if form.validate_on_submit():
        try:
            new_holiday = Holiday(
                country = form.country.data,
                event_date = form.event_date.data,
                description = form.description.data,
                recurring = form.recurring.data
            )
            db.session.add(new_holiday)
            db.session.commit()
            flash('Holiday created successfully!', 'success')
            return redirect(url_for("holiday.index"))
        except SQLAlchemyError as e:
            flash('Problem occurred when creating holiday', 'error')
            current_app.logger.error('Error: %s', e)
            current_app.logger.info(f"Post data: {form.data}")
            db.session.rollback()
        finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")

    return render_template(
        "holiday/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('holiday.create_post')
    )

@bp.route("/holidays/edit/<int:id>", methods=["GET"])
@login_required
def edit(id):
    navform = NavForm()
    prevnextform = PrevNextForm()

    try:
        holiday = db.session.get(Holiday, id)            
        if not holiday:
            raise SQLAlchemyError("Holiday not found")

    except SQLAlchemyError as e:
        flash('Holiday not found')
        current_app.logger.error('Error: %s', e)
        return redirect(url_for("holiday.index"))

    form = HolidayForm(obj=holiday)
    
    return render_template(
        'holiday/create.html', 
        form=form,
        navform=navform, 
        prevnextform=prevnextform,
        action_url=url_for('holiday.edit_post')
    )


@bp.route("/holidays/edit", methods=["POST"])
@login_required
def edit_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = HolidayForm()

    if form.validate_on_submit():
            try:
                holiday = db.session.get(Holiday, form.id.data)
                if holiday:
                    holiday.country = form.country.data,
                    holiday.event_date = form.event_date.data,
                    holiday.description = form.description.data,
                    holiday.recurring = form.recurring.data
                    db.session.commit()
                    return redirect(url_for("holiday.index"))
            except SQLAlchemyError as e:
                flash('Problem occured when updating holiday record')
                current_app.logger.error('Error: %s', e)
                db.session.rollback()
            finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")       
    
    return render_template(
        "holiday/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('holiday.edit_post')
    )


@bp.route("/holidays/delete/<int:id>", methods=("GET","POST"))
@login_required
def delete(id):
    try:
        Holiday.query.filter(Holiday.id == id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Database error has occured when attempting delete")
        current_app.logger.error(f"Error: {e}")

    return redirect(url_for("holiday.index"))
