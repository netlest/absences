from flask import Blueprint, current_app, render_template, url_for, flash, redirect
from flask_login import login_required, current_user
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
from ..extensions import db
from ..forms import UserForm, NavForm, PrevNextForm
from ..models import User, Group, UserGroup

bp = Blueprint("user", __name__)

@bp.before_request
@login_required
def restrict_to_admins():
    if  not current_user.admin:
        flash('You do not have permission to view this page', 'error')
        return redirect(url_for('main.index'))

@bp.route("/users", methods=["GET"])
@login_required
def index():
    navform = NavForm()
    prevnextform = PrevNextForm()

    engine = db.get_engine()
    dialect = engine.dialect.name

    # Define the group concatenation function based on the dialect
    if dialect == 'sqlite':
        group_concat = func.group_concat
    elif dialect == 'postgresql':
        group_concat = func.string_agg
    else:
        raise ValueError(f"Unsupported database dialect: {dialect}")

    users = db.session.query(
        User.id,
        User.username,
        group_concat(Group.name, ', ').label('groups')
        # func.string_agg(Group.name, ', ').label('groups')
    ).outerjoin(UserGroup, User.id == UserGroup.user_id)\
    .outerjoin(Group, UserGroup.group_id == Group.id)\
    .group_by(User.id, User.username)\
    .order_by(User.username).all()

    return render_template(
        "user/index.html", 
        users=users,
        navform=navform,
        prevnextform=prevnextform
    )

@bp.route("/users/create", methods=["GET"])
@login_required
def create():
    form = UserForm(is_edit=False)
    navform = NavForm()
    prevnextform = PrevNextForm()
    return render_template(
        'user/create.html', 
        form=form, 
        navform=navform, 
        prevnextform=prevnextform, 
        action_url=url_for('user.create_post')
    )

@bp.route("/users/edit/<int:id>", methods=["GET"])
@login_required
def edit(id):
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = UserForm()

    try:
        user = db.session.get(User, id)

        groups = db.session.query(Group).join(UserGroup).filter(
            UserGroup.user_id == id,
            UserGroup.group_id == Group.id
        ).distinct().all()

    except SQLAlchemyError as e:
        flash('Error getting user data from database')
        current_app.logger.error(e)
        return redirect(url_for("user.index"))

    form = UserForm(is_edit=True, obj=user)
    form.groups.process_data([g.id for g in groups])

    return render_template(
        'user/create.html', 
        form=form, 
        navform=navform, 
        prevnextform=prevnextform, 
        action_url=url_for('user.edit_post')
    )

@bp.route("/users/create", methods=['POST'])
@login_required
def create_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = UserForm(is_edit=False)

    if form.validate_on_submit():
        try:
            new_user = User(
                username=form.username.data,
                password=generate_password_hash(form.password.data)
            )
            db.session.add(new_user)
            db.session.flush()  # Push the user to the database to get its ID

            for group_id in form.groups.data:
                user_group = UserGroup(user_id=new_user.id, group_id=group_id)
                db.session.add(user_group)

            db.session.commit()

            flash('User created successfully!', 'success')
            return redirect(url_for("user.index"))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {e}")
            flash('Problem occurred when creating user and adding to groups', 'danger')
        finally:
            db.session.close()
            
    return render_template(
        'user/create.html',
        form=form, 
        navform=navform, 
        prevnextform=prevnextform,
        action_url=url_for('user.create_post')
    )


@bp.route("/users/edit", methods=["POST"])
@login_required
def edit_post():
    navform = NavForm()
    prevnextform = PrevNextForm()
    form = UserForm(is_edit=True)

    if form.validate_on_submit():
        try:
            user = User.query.get_or_404(form.id.data)

            # Delete existing user groups
            UserGroup.query.filter_by(user_id=form.id.data).delete()

            # Add user to selected groups
            for group_id in form.groups.data:
                user_group = UserGroup(user_id=form.id.data, group_id=group_id)
                db.session.add(user_group)

            # Update user data
            user.username = form.username.data
            if form.password.data:
                user.password = generate_password_hash(form.password.data)

            db.session.commit()

            flash('User updated successfully!', 'success')
            return redirect(url_for("user.index"))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Problem occured when updating user')
            current_app.logger.error('Error: %s', e)

        finally:
            db.session.close()

    return render_template(
        'user/create.html', 
        form=form, 
        navform=navform, 
        prevnextform=prevnextform,
        action_url=url_for('user.edit_post')
    )

@bp.route("/users/delete/<int:id>", methods=("GET","POST"))
@login_required
def delete(id):
    if id==current_user.id:
        flash("You cannot delete the currently logged in user")
        return redirect(url_for("user.index"))
    
    if id==1:
        flash("You cannot delete the admin user")
        return redirect(url_for("user.index"))
    
    try:
        User.query.filter(User.id == id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Database error has occured when attempting delete user")
        current_app.logger.error(f"Error: {e}")

    return redirect(url_for("user.index"))

