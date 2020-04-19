import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    # the columns for each task
    # description
    description = db.Column(db.String, nullable=False)
    # done or not
    completed = db.Column(db.Boolean, default=False)
    # date and time created
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # date and time done
    date_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    # user
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
