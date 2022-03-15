from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired,Email,InputRequired, Length

class RegisterForm(FlaskForm):
    fname = StringField('firstname', validators=[InputRequired()])
    lname = StringField('lastname', validators=[InputRequired()])
    email = StringField('email', validators=[InputRequired(), Email(message='email not valid')])
    password = PasswordField('password',validators=[InputRequired(), Length(min=6)])
    address = StringField('address', validators=[InputRequired()])
    phone = StringField('phone', validators=[InputRequired()])

class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='email not valid')])
    password = PasswordField('password',validators=[InputRequired(), Length(min=6)])