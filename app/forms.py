from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, DateField, SelectField, ColorField, SelectMultipleField
from wtforms import BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from wtforms.widgets import HiddenInput
from wtforms.validators import ValidationError
from flask import session, current_app
from flask_login import current_user
from datetime import datetime
from .models import User, Group, UserGroup, Absence, Object
from .extensions import db

def no_whitespace(form, field):
    if any(char.isspace() for char in field.data):
        raise ValidationError('Spaces are not allowed here')

def validate_abs_date_end(form, field):
    if field.data < form.abs_date_start.data:
        raise ValidationError('End date must be the same day or in the future compared to start date.')

def validate_user_exists(form, field):
    user = User.query.filter_by(username=field.data).first()
    if user:
        raise ValidationError('User already exists')

def validate_group_exists(form, field):
    group = Group.query.filter_by(name=field.data).first()
    if group:
        raise ValidationError('Group with that name already exists')

# Validate if object someone is trying to modify absence belongs to any of the user's groups
def validate_abs_group(form, field):
    obj = db.session.get(Object, field.data)

    user_groups = db.session.query(Group).join(UserGroup).filter(
        UserGroup.user_id == current_user.id,
        UserGroup.group_id == Group.id
    ).distinct().all()

    if obj.group_id not in [group.id for group in user_groups]:
        raise ValidationError('This object does not belong to any of your groups')

# Validate if object owner is the current user attempting to modify the absence
# Note: This validation is only applied if MODIFY_ALL_GROUP_ABSENCES is set to False
def validate_abs_owner(form, field):

    new_obj = db.session.get(Object, field.data)
    absence_id = form.id.data if 'id' in form else None

    if not current_app.config['MODIFY_ALL_GROUP_ABSENCES']:
        # Edit mode
        if absence_id:
            # Check if the absence exists and get the original object
            # If current absence object owner is not the current user, raise an error not allowing the modification
            absence = db.session.get(Absence, absence_id)
            if absence.object.user_id != current_user.id:
                    raise ValidationError('You do not have permission to modify absence for this object')
        else:
            # For new absences, validate ownership of the object chosen
            if new_obj.user_id != current_user.id:
                raise ValidationError('You do not have permission to create an absence for this object')


def validate_date_overlap(form, field):
    query = db.session.query(Absence).filter(
        Absence.object_id == form.object_id.data,
        Absence.abs_date_start >= form.abs_date_start.data,
        Absence.abs_date_end <= form.abs_date_end.data
    )

    # Edit mode - exclude current record from the query
    query = query.filter(Absence.id != form.id.data)

    if query.count() > 0:
        raise ValidationError('Absence dates overlap with an existing record')
    
class ObjectForm(FlaskForm):
    id =  IntegerField(widget=HiddenInput(), validators=[Optional()])

    object_name = StringField('Name', validators=[DataRequired(),
                                        Length(min=2, max=30)])

    group_id = SelectField('Group', coerce=int, choices=[], validators=[DataRequired()])
    
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Submit')

    @classmethod
    def get_group_choices(cls):
        with current_app.app_context():
            groups = db.session.query(Group).join(UserGroup).filter(
                UserGroup.user_id == current_user.id,
                UserGroup.group_id == Group.id
            ).distinct().all()
            group_choices = [(g.id, g.name) for g in groups]
            return group_choices
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_id.choices = self.get_group_choices()


class TypesForm(FlaskForm):
    id = IntegerField(widget=HiddenInput(), validators=[Optional()])

    name = StringField('Name', validators=[DataRequired(),
                                           Length(min=2, max=30)])
    color = ColorField('Color', validators=[DataRequired(),
                                              Length(min=2, max=20)])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    id = IntegerField(widget=HiddenInput(), validators=[Optional()])
    username = StringField('Username')
    password = PasswordField('Password')

    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])

    groups = SelectMultipleField('Groups', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')

    @classmethod
    def get_group_choices(cls):
        with current_app.app_context():
            groups = db.session.query(Group).all()
            group_choices = [(g.id, g.name) for g in groups]
            return group_choices
        
    def __init__(self, *args, **kwargs):
        is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # Set dynamic validators depends if we are creating or editing
        if is_edit:
            self.username.validators = [DataRequired(), Length(min=2, max=30), no_whitespace]
            # Password is optional for editing
            self.password.validators = [Optional()]
            self.confirm_password.validators = [Optional()]
        else:
            self.username.validators = [DataRequired(), Length(min=2, max=30), no_whitespace, validate_user_exists]
            # Password is required for creating
            self.password.validators = [DataRequired(), Length(min=5, max=50)]
            self.confirm_password.validators = [
                DataRequired(),
                EqualTo('password', message='Passwords must match')
            ]

        self.groups.choices = self.get_group_choices()



class GroupForm(FlaskForm):
    id = IntegerField(widget=HiddenInput(), validators=[Optional()])

    # user_id = SelectField('Owner', coerce=int, choices=[], validators=[DataRequired()])

    name = StringField('Name', validators=[DataRequired(), validate_group_exists,       
                                        Length(min=2, max=30)])
    description = StringField('Description', validators=[DataRequired(),
                                                Length(min=2, max=255)])        
    submit = SubmitField('Submit')

class HolidayForm(FlaskForm):
    id = IntegerField(widget=HiddenInput(), validators=[Optional()])

    country = StringField('Country code', validators=[DataRequired(),
                                          Length(min=2, max=4),
                                          no_whitespace
                                          ])

    event_date = DateField('Data', validators=[DataRequired()])

    recurring = BooleanField('Mark recurring', validators=[])

    description = StringField('Event description', validators=[DataRequired(),
                                                  Length(min=2, max=30)])

    submit = SubmitField('Submit')

class AbsenceForm(FlaskForm):
    id = IntegerField(widget=HiddenInput(), validators=[Optional()])

    object_id = SelectField(
        'Object',
        coerce=int,
        choices=[],  # Placeholder for dynamic population
        validators=[DataRequired(), validate_abs_group, validate_abs_owner]
    )

    type_id = SelectField(
        'Absence Type',
        coerce=int,
        choices=[],  # Placeholder for dynamic population
        validators=[DataRequired()]
    )

    abs_date_start = DateField('Date begin', validators=[DataRequired(), validate_date_overlap])
    abs_date_end = DateField('Date end', validators=[DataRequired(), validate_abs_date_end, validate_date_overlap])

    description = StringField('Description', validators=[Optional()])

    submit = SubmitField('Save')


class PrevNextForm(FlaskForm):
    prev = SubmitField('Prev')
    next = SubmitField('Next')
    

class NavForm(FlaskForm):
    chunksize = SelectField('Chunksize', 
                            coerce=int,
                            choices=[],
                            validators=[DataRequired()]
                            )
    
    start_month = SelectField('Start month', 
                              coerce=int, 
                              choices=[],
                              validators=[DataRequired()]
                              )
    
    start_year = SelectField('Start year', 
                             coerce=int, 
                             choices=[],
                             validators=[DataRequired()]
                             )
    
    group_id = SelectField('Group id', coerce=int, choices=[], validators=[DataRequired()], id='group_id')
    submit_btn = SubmitField('Show me!')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        chunksize = session.get("chunksize", 4)
        start_month = session.get("start_month", datetime.today().month)
        start_year = session.get("start_year", datetime.today().year)
        group_id = session.get("group_id", 1)

        chunksize_choices = [(str(i), i) for i in range(1, 14)]
        start_month_choices = [(str(i), i) for i in range(1, 13)]
        start_year_choices = [(str(year), year) for year in range(start_year - 5, start_year + 6)]

        user_groups = db.session.query(Group).join(UserGroup).filter(
            UserGroup.user_id == current_user.id,
            UserGroup.group_id == Group.id
        ).distinct().all()

        self.chunksize.choices = chunksize_choices
        self.start_month.choices = start_month_choices
        self.start_year.choices = start_year_choices
        self.group_id.choices = [(group.id, group.name) for group in user_groups]

        # Retrieve default values only if the form is not submitted
        if not self.is_submitted():
            self.chunksize.data = chunksize
            self.start_month.data = start_month
            self.start_year.data = start_year
            self.group_id.data = group_id
