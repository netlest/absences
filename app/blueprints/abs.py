import os
from datetime import date, datetime
from flask import Blueprint, current_app, request, render_template, url_for, flash, redirect, session
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, cast, Integer
from werkzeug.utils import redirect as safe_redirect
from ..extensions import db
from ..forms import AbsenceForm, NavForm, PrevNextForm
from ..models import Absence, AbsenceType, Object, Group, User

bp = Blueprint("abs", __name__)

@bp.route("/absences")
@login_required
def index():
    navform = NavForm()
    prevnextform = PrevNextForm()

    engine = db.get_engine()
    dialect = engine.dialect.name

    # Define the duration calculation based on the dialect
    if dialect == 'sqlite':
        duration = cast(func.julianday(Absence.abs_date_end) - func.julianday(Absence.abs_date_start) + 1, Integer)
    elif dialect == 'postgresql':
        duration = Absence.abs_date_end - Absence.abs_date_start + 1
    else:
        raise ValueError(f"Unsupported database dialect: {dialect}")



    query = db.session.query(
        Absence.id,
        Absence.object_id,
        Object.name.label('object_name'),
        Object.user_id,
        Group.name.label('group_name'),
        Absence.type_id,
        Absence.abs_date_start,
        Absence.abs_date_end,
        duration.label('duration'),
        # (Absence.abs_date_end - Absence.abs_date_start + 1).label('duration'),
        Absence.description,
        AbsenceType.color.label('at_color'),
        AbsenceType.name.label('at_name')
    ).outerjoin(AbsenceType, Absence.type_id == AbsenceType.id)\
     .outerjoin(Object, Absence.object_id == Object.id)\
     .join(Group, Object.group_id == Group.id)\
     .order_by(Group.name, Absence.abs_date_start.desc())

    # If user is not admin filter only absences related to user's groups
    if not current_user.admin:
        query = query.filter(Object.group_id.in_([group.id for group in current_user.groups]))

    absences = query.all()

    return render_template(
        "abs/index.html", 
        absences=absences,
        navform=navform,
        prevnextform=prevnextform
    )


@bp.route("/absences/create", methods=["GET"])
@bp.route("/absences/create/<int:object_id>/<int:day>/<int:month>/<int:year>/<int:goback>", methods=["GET"])
@login_required
def create(object_id=None, day=None, month=None, year=None, goback=0):
    navform = NavForm()
    prevnextform = PrevNextForm()

    # Store the referrer in the session
    if 'referrer' not in session and goback==1:
        session['referrer'] = request.referrer

    abs_types = db.session.query(AbsenceType).all()
    absence_types = [(str(abs_type.id), abs_type.name) for abs_type in abs_types]   # Convert to list of tuples

    object_query = Object.query.filter(
        Object.group_id.in_([group.id for group in current_user.groups])
    )

    if not current_app.config['SHOW_ALL_GROUP_OBJECTS']:
        object_query = object_query.filter(Object.user_id == current_user.id)

    objects = object_query.all()
    objects_types = [(str(obj.id), obj.group.name+" " + obj.name) for obj in objects]    # Convert to list of tuples

    input_data = {
        'object_id': object_id,
        'abs_date_start': datetime(year, month, day) if all([day, month, year]) else date.today(),
        'abs_date_end': datetime(year, month, day) if all([day, month, year]) else date.today()
    }

    form = AbsenceForm(data=input_data)
    form.type_id.choices = absence_types
    form.object_id.choices = objects_types

    return render_template(
        "abs/create.html",
        form=form, 
        navform=navform, prevnextform=prevnextform,
        action_url=url_for('abs.create_post')
    )

@bp.route("/absences/create", methods=["POST"])
@login_required
def create_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = AbsenceForm()

    abs_types = db.session.query(AbsenceType).all()
    absence_types = [(str(abs_type.id), abs_type.name) for abs_type in abs_types]

    object_query = Object.query.filter(
        Object.group_id.in_([group.id for group in current_user.groups])
    )

    if not current_app.config['SHOW_ALL_GROUP_OBJECTS']:
        object_query = object_query.filter(Object.user_id == current_user.id)

    objects = object_query.all()
    objects_types = [(str(obj.id), obj.group.name+" " + obj.name) for obj in objects]    # Convert to list of tuples

    form.object_id.choices = objects_types
    form.type_id.choices = absence_types


    if form.validate_on_submit():
        try:
            new_absence = Absence(
                object_id=form.object_id.data,
                type_id=form.type_id.data,
                abs_date_start=form.abs_date_start.data,
                abs_date_end=form.abs_date_end.data,
                description=form.description.data
            )
            db.session.add(new_absence)
            db.session.commit()
            flash('New absence registered', 'success')

            referrer = session.pop('referrer', None)
            current_app.logger.info(f"Redirecting to: {referrer or url_for('abs.index')}")
            return safe_redirect(referrer or url_for("main.index"))

        except SQLAlchemyError as e:
            flash('Problem occurred when creating absence', 'error')
            current_app.logger.error('Error: %s', e)
            current_app.logger.info(f"Post data: {form.data}")
            db.session.rollback()
        finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")

    return render_template(
        "abs/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('abs.create_post')
    )

@bp.route("/absences/edit/<int:id>", methods=["GET"])
@login_required
def edit(id):
    navform = NavForm()
    prevnextform = PrevNextForm()

    abs_types = db.session.query(AbsenceType).all()
    absence_types = [(str(abs_type.id), abs_type.name) for abs_type in abs_types]   # Convert to list of tuples

    object_query = Object.query.filter(
        Object.group_id.in_([group.id for group in current_user.groups])
    )

    if not current_app.config['SHOW_ALL_GROUP_OBJECTS']:
        object_query = object_query.filter(Object.user_id == current_user.id)

    objects = object_query.all()
    objects_types = [(str(obj.id), obj.group.name+" " + obj.name) for obj in objects]    # Convert to list of tuples

    try:
        absence = db.session.get(Absence, id)     

        if not current_app.config['MODIFY_ALL_GROUP_ABSENCES']:
            if absence.object.user_id != current_user.id:
                flash('You do not have permission to edit this absence.', 'error')
                return redirect(url_for("abs.index"))

        if not absence:
            raise SQLAlchemyError("Absence not found")
        
        form = AbsenceForm(obj=absence)
        form.type_id.choices = absence_types
        form.object_id.choices = objects_types

    except SQLAlchemyError as e:
        flash('Exception occurred when attempting to edit absence')
        current_app.logger.error('Error: %s', e)
        return redirect(url_for("abs.index"))
    
    return render_template(
        "abs/create.html",
        absence=absence,
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('abs.edit_post')
    )

@bp.route("/absences/edit", methods=["POST"])
@login_required
def edit_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = AbsenceForm()

    abs_types = db.session.query(AbsenceType).all()
    absence_types = [(str(abs_type.id), abs_type.name) for abs_type in abs_types]

    object_query = Object.query.filter(
        Object.group_id.in_([group.id for group in current_user.groups])
    )

    if not current_app.config['SHOW_ALL_GROUP_OBJECTS']:
        object_query = object_query.filter(Object.user_id == current_user.id)

    objects = object_query.all()
    objects_types = [(str(obj.id), obj.group.name+" " + obj.name) for obj in objects]    # Convert to list of tuples

    form.object_id.choices = objects_types
    form.type_id.choices = absence_types

    if form.validate_on_submit():
            try:
                absence = db.session.get(Absence, form.id.data)

                if absence:
                    absence.object_id=form.object_id.data
                    absence.type_id=form.type_id.data
                    absence.abs_date_start=form.abs_date_start.data
                    absence.abs_date_end=form.abs_date_end.data
                    absence.description=form.description.data
                    db.session.commit()
                    return redirect(url_for("main.index"))
            except SQLAlchemyError as e:
                flash('Problem occured when updating absence')
                current_app.logger.error('Error: %s', e)
                db.session.rollback()
            finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")    

    return render_template(
        'abs/create.html',
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('abs.edit_post')
    )


@bp.route("/absences/delete/<int:id>", methods=("GET","POST"))
@login_required
def delete(id):

    user = User.query.get_or_404(current_user.id)
    user_groups = [(group.id, group.name) for group in user.groups]
    absence = Absence.query.get(id)

    if absence:
        if current_user.admin:
            # Admin can delete any absence
            db.session.delete(absence)
            db.session.commit()
        else:
            # Check if user is allowed to delete absence related to all group objects 
            if current_app.config['MODIFY_ALL_GROUP_ABSENCES']:

                if absence.object.group_id in [group[0] for group in user_groups]:
                    db.session.delete(absence)
                    db.session.commit()
                else:
                    flash('This absence is not related to any of your groups. You cannot delete it', 'error')
                    return redirect(url_for("main.index"))
                
            else:
                # User can delete absence related to their owned objects
                if absence.object.user_id == current_user.id:
                    db.session.delete(absence)
                    db.session.commit()
                else:
                    flash('You do not have permission to delete this absence.', 'error')
                    return redirect(url_for("main.index"))
        
        flash(f'Absence deleted successfully', 'success')
    else:
        flash('Absence not found.', 'error')

    return redirect(url_for("main.index"))

