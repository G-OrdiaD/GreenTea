from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo,NumberRange, ValidationError
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    FloatField,
    BooleanField
)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])  # Added Email validator
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')  # Added missing submit button

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ParameterForm(FlaskForm):
    name = SelectField('Parameter', choices=[
        ('temperature', 'Temperature'),
        ('humidity', 'Humidity'),
        ('ph', 'pH'),
        ('air_quality', 'Air Quality'),
        ('light', 'Light Intensity')
    ], validators=[DataRequired()])
    min_value = FloatField('Minimum Value', validators=[DataRequired()])
    max_value = FloatField('Maximum Value', validators=[DataRequired()])
    unit = SelectField('Unit', choices=[
        ('°C', '°C'),
        ('%', '%'),
        ('level', 'level'),
        ('ppm', 'ppm'),
        ('lux', 'lux')
    ], validators=[DataRequired()])
    submit = SubmitField('Save')

    def validate_max_value(form, field):
        if field.data <= form.min_value.data:
            raise ValidationError('Maximum value must be greater than minimum value')

    max_value = FloatField('Maximum Value', validators=[
        DataRequired(),
        NumberRange(min=0),
        validate_max_value
    ])

    def validate_name(form, field):
        if SensorParameter.query.filter_by(name=field.data).first():
            raise ValidationError('Parameter already exists')