from flask import Blueprint, current_app, render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
from ..forms import GroupForm, NavForm, PrevNextForm
from ..models import Group, User


bp = Blueprint("group", __name__)

@bp.before_request
@login_required
def restrict_to_admins():
    if  not current_user.admin:
        flash('You do not have permission to view this page', 'error')
        return redirect(url_for('main.index'))
    
@bp.route("/groups")
@login_required
def index():
    navform = NavForm()
    prevnextform = PrevNextForm()

    groups = db.session.query(
        Group.id,
        User.username.label('owner'),
        Group.name,
        Group.description
    ).outerjoin(User, Group.user_id == User.id).all()

    return render_template(
        "group/index.html", 
        groups=groups, 
        navform=navform, 
        prevnextform=prevnextform
    )

@bp.route("/groups/create", methods=["GET"])
@login_required
def create():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = GroupForm()
    return render_template(
        "group/create.html", 
        form=form, 
        navform=navform, 
        prevnextform=prevnextform,
        action_url=url_for('group.create_post')
    )

@bp.route("/groups/create", methods=["POST"])
@login_required
def create_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = GroupForm()

    if form.validate_on_submit():
        try:
            new_group = Group(
                user_id=current_user.id,
                name=form.name.data,
                description=form.description.data
            )
            db.session.add(new_group)
            db.session.commit()
            flash('Group created successfully!', 'success')
            return redirect(url_for("group.index"))
        except SQLAlchemyError as e:
            flash('Problem occurred when creating group', 'error')
            current_app.logger.error('Error: %s', e)
            current_app.logger.info(f"Post data: {form.data}")
            db.session.rollback()
        finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")

    return render_template(
        "group/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('group.create_post')
    )

@bp.route("/groups/edit/<int:id>", methods=["GET"])
@login_required
def edit(id):
    navform = NavForm()
    prevnextform = PrevNextForm()

    try:
        group = db.session.get(Group, id)            

        if not group:
            raise SQLAlchemyError("Group not found")

    except SQLAlchemyError as e:
        flash('Group not found')
        current_app.logger.error('Error: %s', e)
        return redirect(url_for("group.index"))

    form = GroupForm(obj=group)
    
    return render_template(
        "group/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('group.edit_post')
    )

@bp.route("/groups/edit", methods=["POST"])
@login_required
def edit_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = GroupForm()

    if form.validate_on_submit():
            try:
                group = db.session.get(Group, form.id.data)
                if group:
                    group.name = form.name.data
                    group.description = form.description.data
                    db.session.commit()
                    return redirect(url_for("group.index"))
            except SQLAlchemyError as e:
                flash('Problem occured when updating group')
                current_app.logger.error('Error: %s', e)
                db.session.rollback()
            finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")       
    
    return render_template(
        "group/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('object.edit_post')
    )

@bp.route("/groups/delete/<int:id>", methods=("GET","POST"))
@login_required
def delete(id):

    if id==1:
        flash("You cannot delete default group")
        return redirect(url_for("group.index"))

    try:
        Group.query.filter(Group.id == id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Database error has occured when attempting delete")
        current_app.logger.error(f"Error: {e}")

    return redirect(url_for("group.index"))

