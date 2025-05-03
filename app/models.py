from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(70), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(80), unique=True)
    role = db.Column(db.String(25), default='employee')

    assigned_greenhouses = db.relationship('GreenhouseAssignment', backref='employee', lazy=True)
    feedback = db.relationship('Feedback', backref='author', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_id(self):
        return str(self.id)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_admin(self):
        return self.role == 'admin'


class Greenhouse(db.Model):
    __tablename__ = 'greenhouses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(200))

    assignments = db.relationship('GreenhouseAssignment', backref='assignment_greenhouse', lazy=True)
    sensor_data = db.relationship('SensorData', backref='greenhouse', lazy=True, overlaps="all_sensor_data")
    issues = db.relationship('Issue', back_populates='greenhouse', lazy=True)


class GreenhouseAssignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    greenhouse_id = db.Column(db.Integer, db.ForeignKey('greenhouses.id'))
    assigned_on = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)


class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id = db.Column(db.Integer, primary_key=True)
    greenhouse_id = db.Column(db.Integer, db.ForeignKey('greenhouses.id'))
    parameter_id = db.Column(db.Integer, db.ForeignKey('sensor_parameter.id'))
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    parameter = db.relationship('SensorParameter', backref='readings')


class SensorParameter(db.Model):
    __tablename__='sensor_parameter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    min_value = db.Column(db.Float, nullable=False)
    max_value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(15))

class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer, primary_key=True)
    greenhouse_id = db.Column(db.Integer, db.ForeignKey('greenhouses.id'), nullable=False)
    parameter_id = db.Column(db.Integer, db.ForeignKey('sensor_parameter.id'), nullable=False)
    sensor_type = db.Column(db.String(20))
    current_value = db.Column(db.Float)
    status = db.Column(db.String(20), default='open')
    priority = db.Column(db.String(20))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    parameter = db.relationship('SensorParameter', backref='issues')
    greenhouse = db.relationship('Greenhouse', back_populates='issues')
    assignee = db.relationship('User', backref='assigned_issues')


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class OptimalRange(db.Model):
    __tablename__ = 'optimal_ranges'
    id = db.Column(db.Integer, primary_key=True)
    parameter = db.Column(db.String(50), nullable=False)
    min_value = db.Column(db.Float, nullable=False)
    max_value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<OptimalRange(parameter={self.parameter}, min_value={self.min_value}, max_value={self.max_value})>"