from flask_login import UserMixin
from sqlalchemy import MetaData
from .extensions import db

excluded_metadata = MetaData()

class VAbsence(db.Model):
    __tablename__ = 'v_absences'
    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer)
    group_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    type_id = db.Column(db.Integer)
    abs_date_start = db.Column(db.Date)
    abs_date_end = db.Column(db.Date)
    duration = db.Column(db.Integer)
    description = db.Column(db.String)
    at_color = db.Column(db.String)
    at_name = db.Column(db.String)
    metadata = excluded_metadata  # Assign to the separate metadata object as this is view only

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    groups = db.relationship('Group', secondary='user_groups', backref='users')
    objects = db.relationship('Object', backref='users')

    def __repr__(self):
        return f"<User {self.username}>"

    def get_user_groups(self):
        return self.groups
    
    def get_user_objects(self):
        return self.objects

    # Return absences related to the user owned objects
    def get_related_user_absences(self):
       return Absence.query.join(Object).filter(Object.user_id == self.id).all()

    # Return absences related to groups the user is a member of
    def get_related_group_absences(self):
       return Absence.query.join(Object, Absence.object_id == Object.id)\
        .join(Group, Object.group_id == Group.id)\
        .join(UserGroup, Group.id == UserGroup.group_id)\
        .filter(UserGroup.user_id == self.id).all()

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    objects = db.relationship('Object', back_populates='group', cascade='all, delete-orphan')    # Delete all objects in the group when the group is deleted

    def __repr__(self):
        return f"<Group {self.name}>"

    def get_group_objects(self):
        return self.objects

class Object(db.Model):
    __tablename__ = 'objects'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'))
    name = db.Column(db.String(30), unique=False, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    absences = db.relationship('Absence', back_populates='object', cascade='all, delete-orphan')
    group = db.relationship('Group', back_populates='objects')

    def __repr__(self):
        return f"<Object {self.name}>"

    def get_object_absences(self):
        return self.absences

class AbsenceType(db.Model):
    __tablename__ = 'absence_types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(30))

class Absence(db.Model):
    __tablename__ = 'absences'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    object_id = db.Column(db.Integer, db.ForeignKey('objects.id', ondelete='CASCADE'))
    type_id = db.Column(db.Integer, db.ForeignKey('absence_types.id', ondelete='CASCADE'))
    abs_date_start = db.Column(db.Date, nullable=False)
    abs_date_end = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(150))
    object = db.relationship('Object', back_populates='absences')

    # Return ID of the user who owns the object the absence is related to
    def get_user_id(self):
        return self.object.user_id

    # Return group id of the group the object the absence is related to belongs to
    def get_group_id(self):
        return self.object.group_id

class UserGroup(db.Model):
    __tablename__ = 'user_groups'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)

class Holiday(db.Model):
    __tablename__ = 'holidays'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country = db.Column(db.String(4), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(150))
    recurring = db.Column(db.Boolean, default=False)
