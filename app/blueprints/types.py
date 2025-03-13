from flask import Blueprint, request, render_template, url_for, flash, redirect, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
from ..forms import TypesForm, NavForm, PrevNextForm
from ..models import AbsenceType


bp = Blueprint("types", __name__)

@bp.route("/types")
@login_required
def index():
    navform = NavForm()
    prevnextform = PrevNextForm()
    absence_types = db.session.query(AbsenceType).all()
    return render_template(
        "types/index.html", 
        absence_types=absence_types, 
        navform=navform, 
        prevnextform=prevnextform
    )

@bp.route("/types/create", methods=["GET"])
@login_required
def create():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = TypesForm()
    return render_template(
        'types/create.html',
        form=form, 
        navform=navform, prevnextform=prevnextform,
        action_url=url_for('types.create_post')
    )

@bp.route("/types/create", methods=["POST"])
@login_required
def create_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = TypesForm()

    if form.validate_on_submit():
        try:
            new_type = AbsenceType(
                name=form.name.data,
                color=form.color.data
            )
            db.session.add(new_type)
            db.session.commit()
            flash('Type created successfully!', 'success')
            return redirect(url_for("types.index"))
        except SQLAlchemyError as e:
            flash('Problem occurred when creating absence type', 'error')
            current_app.logger.error('Error: %s', e)
            current_app.logger.info(f"Post data: {form.data}")
            db.session.rollback()
        finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")

    return render_template(
        "types/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('types.create_post')
    )

@bp.route("/types/edit/<int:id>", methods=["GET"])
@login_required
def edit(id):
    navform = NavForm()
    prevnextform = PrevNextForm()

    try:
        absence_type = db.session.get(AbsenceType, id)            
        if not absence_type:
            raise SQLAlchemyError("Group not found")

    except SQLAlchemyError as e:
        flash('Record not found')
        current_app.logger.error('Error: %s', e)
        return redirect(url_for("types.index"))

    form = TypesForm(obj=absence_type)
    
    return render_template(
        'types/create.html', 
        form=form,
        navform=navform, 
        prevnextform=prevnextform,
        action_url=url_for('types.edit_post')
    )


@bp.route("/types/edit", methods=["POST"])
@login_required
def edit_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = TypesForm()

    if form.validate_on_submit():
            try:
                absence_type = db.session.get(AbsenceType, form.id.data)
                if absence_type:
                    absence_type.name = form.name.data
                    absence_type.color = form.color.data
                    db.session.commit()
                    return redirect(url_for("types.index"))
            except SQLAlchemyError as e:
                flash('Problem occured when updating absence type')
                current_app.logger.error('Error: %s', e)
                db.session.rollback()
            finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")       
    
    return render_template(
        "types/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('types.edit_post')
    )

@bp.route("/types/delete/<int:id>", methods=("GET","POST"))
@login_required
def delete(id):
    try:
        AbsenceType.query.filter(AbsenceType.id == id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Database error has occured when attempting delete")
        current_app.logger.error(f"Error: {e}")

    return redirect(url_for("types.index"))

