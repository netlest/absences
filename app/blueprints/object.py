from flask import Blueprint, current_app, render_template, url_for, session, flash, redirect
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from ..extensions import db
from ..forms import ObjectForm, NavForm, PrevNextForm
from ..models import Object, Group, User

bp = Blueprint("object", __name__)

@bp.route("/objects")
@login_required
def index():
    navform = NavForm()
    prevnextform = PrevNextForm()

    query = db.session.query(
        Object.id,
        Object.user_id,
        Object.group_id,
        User.username.label('owner'),
        Group.name.label('group_name'),
        Object.name.label('object_name'),
        Object.description
    ).outerjoin(Group, Object.group_id == Group.id)\
    .outerjoin(User, Object.user_id == User.id)

    # If user is not admin filter only user objects
    if not current_user.admin:
        if current_app.config['SHOW_ALL_GROUP_OBJECTS']:
            query = query.filter(Object.group_id.in_([group.id for group in current_user.groups]))
        else:
            query = query.filter(Object.user_id == current_user.id)

    objects = query.all()

    return render_template(
        "object/index.html", 
        objects=objects, 
        navform=navform, 
        prevnextform=prevnextform
    )

@bp.route("/objects/create", methods=["GET"])
@login_required
def create():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = ObjectForm()
    form.group_id.data = session.get('group_id',1)

    return render_template(
        'object/create.html',
        form=form, 
        navform=navform, prevnextform=prevnextform,
        action_url=url_for('object.create_post')
    )

@bp.route("/objects/edit/<int:id>", methods=["GET"])
@login_required
def edit(id):
    navform = NavForm()
    prevnextform = PrevNextForm()

    try:

        query = db.session.query(
            Object.id,
            Object.user_id,
            Object.group_id,
            User.username.label('owner'),
            Group.name.label('group_name'),
            Object.name.label('object_name'),
            Object.description
        ).outerjoin(Group, Object.group_id == Group.id)\
        .outerjoin(User, Object.user_id == User.id)
        
        # If user is not admin filter only user objects
        if not current_user.admin:
            query = query.filter(Object.user_id == current_user.id, Object.id == id)
        
        record = query.first()

        if not record:
            raise SQLAlchemyError("Record not found or you don't have permission to edit it.")

    except SQLAlchemyError as e:
        flash(f"{e}")
        current_app.logger.error('Error: %s', e)
        return redirect(url_for("object.index"))

    form = ObjectForm(obj=record)
    
    return render_template(
        'object/create.html', 
        form=form,
        navform=navform, 
        prevnextform=prevnextform,
        action_url=url_for('object.edit_post')
    )

@bp.route("/objects/edit", methods=["POST"])
@login_required
def edit_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = ObjectForm()

    if form.validate_on_submit():
            try:
                obj = db.session.get(Object, form.id.data)
                if obj:
                    obj.name = form.object_name.data
                    obj.description = form.description.data
                    obj.group_id = form.group_id.data
                    db.session.commit()
                    return redirect(url_for("object.index"))
            except SQLAlchemyError as e:
                flash('Problem occured when updating object')
                current_app.logger.error('Error: %s', e)
                db.session.rollback()
            finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")       
    
    return render_template(
        'object/create.html',
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('object.edit_post')
    )

@bp.route("/objects/create", methods=["POST"])
@login_required
def create_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = ObjectForm()

    if form.validate_on_submit():
        try:
            new_object = Object(
                user_id=current_user.id,
                group_id=form.group_id.data,
                name=form.object_name.data,
                description=form.description.data
            )
            db.session.add(new_object)
            db.session.commit()
            flash('Object created successfully!', 'success')
            return redirect(url_for("object.index"))
        except SQLAlchemyError as e:
            flash('Problem occurred when creating object', 'error')
            current_app.logger.error('Error: %s', e)
            current_app.logger.info(f"Post data: {form.data}")
            db.session.rollback()
        finally:
                db.session.close()
    else:
        current_app.logger.error(f"Validation error: {form.errors}")
        current_app.logger.error(f"Post data: {form.data}")


    return render_template(
        "object/create.html",
        form=form,
        navform=navform,
        prevnextform=prevnextform,
        action_url=url_for('object.create_post')
    )


@bp.route("/objects/delete/<int:id>", methods=("GET","POST"))
@login_required
def delete(id):

    # user = User.query.get_or_404(current_user.id)
    # user_groups = [(group.id, group.name) for group in user.groups]
    obj = Object.query.get(id)

    if object:
        # Admin can delete any object
        if current_user.admin:
            db.session.delete(obj)
            db.session.commit()
        else:

            # Regular user can delete only their own objects
            if obj.user_id == current_user.id:
                db.session.delete(obj)
                db.session.commit()
            else:
                flash("You do not have permission to delete this object. Only the owner can delete it.")

    return redirect(url_for("object.index"))


    # try:
    #     Object.query.filter(Object.id == id).delete()
    #     db.session.commit()
    # except SQLAlchemyError as e:
    #     db.session.rollback()
    #     flash("Database error has occured when attempting delete")
    #     current_app.logger.error(f"Error: {e}")

