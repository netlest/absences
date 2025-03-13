import sys
import os
import time
import click
from datetime import datetime
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError, IntegrityError
from werkzeug.security import generate_password_hash
from .extensions import db
from .models import User, Group, UserGroup, AbsenceType, Object, Holiday, VAbsence

def test_connection(database_url):
    engine = create_engine(database_url)
    try:
        engine = create_engine(database_url)
        with engine.connect():
            return True
    except OperationalError:
        return False
    
def wait_for_database(database_url=None):
    if not database_url:
        database_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    click.echo(f"Waiting for database to be ready: {database_url}")
    while test_connection(database_url) == False:
        click.echo("Database not ready. Waiting for 2 seconds")
        time.sleep(2)
    click.echo(f"Database is ready. {database_url}")

def create_postgres_db_helper():
    db_admin_user = current_app.config['DB_ADMIN_USER']
    db_admin_pass = current_app.config['DB_ADMIN_PASS']
    db_host = current_app.config['DB_HOST']
    db_name = current_app.config['DB_NAME']
    db_user = current_app.config['DB_USER']
    db_pass = current_app.config['DB_PASS']

    database_url = f'postgresql://{db_admin_user}:{db_admin_pass}@{db_host}/postgres'
    admin_engine = create_engine(database_url)

    if db_admin_user  == None or db_admin_pass == None:
        click.echo("No superuser credentials provided. Skipping database creation.")
        click.echo("Set DB_ADMIN_USER and DB_ADMIN_PASS in your environment to create the database.")
        sys.exit(1)
    else:
        wait_for_database(database_url)

    try:
        with admin_engine.connect() as conn:
            conn.execute(text("COMMIT")) 
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
            if not result.fetchone():
                click.echo(f"Database {db_name} does not exist. Creating...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                conn.execute(text(f"CREATE USER {db_user} WITH PASSWORD '{db_pass}'"))
                conn.execute(text(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}"))
                click.echo(f"Database {db_name} created.")
                wait_for_database()
            else:
                click.echo(f"Database {db_name} already exists. Skipping creation.")
    except OperationalError as e:
        click.echo(f"Error connecting to PostgreSQL: {e}")

def init_db_helper():
    wait_for_database()
    engine = db.get_engine()
    dialect = engine.dialect.name

    if dialect == "postgresql":
        view_sql = os.path.join(current_app.root_path, 'sql/view_psql.sql')
    elif dialect == "sqlite":
        view_sql = os.path.join(current_app.root_path, 'sql/view_sqlite.sql')
    else:
        raise ValueError(f"Unsupported database dialect: {dialect}")
    
    # Create all tables from model definitions
    db.create_all()

    # Try to query view capture exception if it doesn't exist
    # Create view if it doesn't exist
    try:
        res=VAbsence.query.first()
    except SQLAlchemyError  as e:
        click.echo("View doesn't exists creating it")

        with open(view_sql, 'r') as file:
            view_script = file.read()
            view_statements = view_script.split(';')

        for statement in view_statements:
            if statement.strip():
                try:
                    db.session.execute(text(statement))
                except ProgrammingError as e:
                    current_app.logger.error(f"Failed to execute statement: {statement}")
                    current_app.logger.error(e)

        db.session.commit()
        click.echo("Tables and views created.")


def populate_db_helper():

    # Create admin user
    password_hash=generate_password_hash("admin")
    admin_user = User(username='admin', password=password_hash, admin=True)
    try:
        db.session.add(admin_user)
        db.session.commit()
        click.echo(f"Admin user created with ID: {admin_user.id}")
    except IntegrityError as e:
        db.session.rollback()
        click.echo("User admin alredy exists. Skipping creation.")

    # Create default group
    default_group = Group(user_id=admin_user.id, name='Default', description='Default group')
    try:
        db.session.add(default_group)
        db.session.commit()
        click.echo(f"Created default group with ID: {default_group.id}")
    except IntegrityError as e:
        db.session.rollback()
        click.echo(f"Group already exists. Skipping creation.")

    # If admin and group was craeted add admin to default group
    if admin_user.id and default_group.id:
        user_group = UserGroup(user_id=admin_user.id, group_id=default_group.id)
        try:
            db.session.add(user_group)
            db.session.commit()
            click.echo(f"Admin user added to default group")
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding admin to default group: {e}")
            click.echo(f"Error adding admin to default group")

        # Insert one object owned by admin
        object = Object(user_id=admin_user.id, group_id=default_group.id, name='Admin', description='Default object owned by admin')
        try:
            db.session.add(object)
            db.session.commit()
            click.echo(f"Added object: {object.name}")
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding object: {e}")
            click.echo(f"Error adding object: {object.name}")   

        # Insert one holiday
        ny_event_date=datetime.strptime('2021-01-01', '%Y-%m-%d').date()
        holiday = Holiday(description="New Year", event_date=ny_event_date, country="pl", recurring=True)
        try:
            db.session.add(holiday)
            db.session.commit()
            click.echo(f"Added holiday: {holiday.description}")
        except IntegrityError as e:
            db.session.rollback()
            click.echo(f"Error adding holiday: {holiday.description}")

    # Insert absence types
    absence_types = {'Other': '#FFA500', 'Vacation': '#CE1616', 'Busy': '#5A5AFF', 'Sick': '#51AC4E', 'Holiday': '#A020F0'}
    for name, color in absence_types.items():
        absence_type = AbsenceType(name=name, color=color)
        try:
            db.session.add(absence_type)
            db.session.commit()
            click.echo(f"Added absence type: {name}")
        except IntegrityError as e:
            db.session.rollback()
            click.echo(f"Absence type: {name} already exists. Skipping creation.")


@click.command(name='test-db-conn', help="Test database connection")
@with_appcontext
def test_db_conn():
    database_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    current_app.logger.info(f"Testing database connection: {database_url}")
    if test_connection(database_url):
        click.echo("Database connection successful")
        sys.exit(0)
    else:
        click.echo("Database connection failed")
        sys.exit(1)



@click.command(name='create-postgres-db', help="Create empty database and role in PostgreSQL")
@with_appcontext
def create_postgres_db():
    create_postgres_db_helper()

@click.command(name='drop-postgres-db', help="Drop PostgreSQL database")
@with_appcontext
def drop_postgres_db():
    db_admin_user = current_app.config['DB_ADMIN_USER']
    db_admin_pass = current_app.config['DB_ADMIN_PASS']
    db_host = current_app.config['DB_HOST']
    db_name = current_app.config['DB_NAME']
    db_user = current_app.config['DB_USER']
    database_url = f'postgresql://{db_admin_user}:{db_admin_pass}@{db_host}/postgres'
    admin_engine = create_engine(database_url)

    try:
        with admin_engine.connect() as conn:
            conn.execute(text("COMMIT")) 
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
            if result.fetchone():
                click.echo("Database exists. Dropping...")
                conn.execute(text(f"""SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity 
                                  WHERE pg_stat_activity.datname = '{db_name}' AND pid <> pg_backend_pid()
                                  """))
               
                conn.execute(text(f"REVOKE all privileges ON DATABASE {db_name} FROM {db_user}"))
                conn.execute(text(f"DROP DATABASE {db_name}"))
                conn.execute(text(f"DROP ROLE {db_user}"))
                
            else:
                click.echo(f"Database {db_name} does not exist.")

    except OperationalError as e:
        click.echo(f"Error connecting to PostgreSQL: {e}")



@click.command('init-db', help="Initialize the database schema.")
@with_appcontext
def init_db_command():
    init_db_helper()

@click.command(name='populate-db', help="Insert initial data into the database")
@with_appcontext
def populate_db():
    populate_db_helper()

@click.command(name='reset-admin', help="Reset admin user password")
@with_appcontext
def reset_admin():
    user = User.query.get_or_404(1)
    password_hash=generate_password_hash("admin")
    try:
        user.password = password_hash
        db.session.commit()
        click.echo("Admin password reset successfully")
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error resetting admin password: {e}")
        click.echo("Error resetting admin password")



@click.command(name="setup-db", help="Create database, initialize schema and populate with initial data")
@with_appcontext
def setup_db():
    database_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    engine = db.get_engine()
    dialect = engine.dialect.name
    current_app.logger.info(f"Database in use: {dialect}")
    current_app.logger.info(f"Testing database connection: {database_url}")

    if test_connection(database_url):
        click.echo("Database connection successful")
    else:
        click.echo("Database connection failed")
        if dialect == "postgresql":
            create_postgres_db_helper()


    init_db_helper()
    populate_db_helper()
    

def init_cli(app):
    app.cli.add_command(create_postgres_db)
    app.cli.add_command(drop_postgres_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_admin)
    app.cli.add_command(populate_db)
    app.cli.add_command(test_db_conn)
    app.cli.add_command(setup_db)