from flask_wtf import FlaskForm
from wtforms import (
    IntegerField, 
    PasswordField, 
    RadioField,
    SelectField,
    StringField, 
    validators
)
from payfriend import db


class RegisterForm(FlaskForm):
    """Form used for registering new users"""
    email = StringField(
        'Email', 
        validators=[validators.InputRequired(), 
                    validators.Email()])
    password = PasswordField(
        'Password', 
        validators=[validators.InputRequired()])
    phone_number = StringField(
        'Phone', 
        validators=[validators.InputRequired()])
    full_phone = StringField('Full Phone')
    channel = RadioField(
        'Channel',
        choices=[('sms', 'SMS'),('call', 'Call')],
        default='sms')

    def create_user(self, authy_user_id):
        user = User(self.email.data, self.password.data, 
                    self.phone_number.data, authy_user_id)

        # Save the user
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


class LoginForm(FlaskForm):
    """Form used for logging in existing users"""
    email = StringField('Email', validators=[validators.InputRequired(), validators.Email()])
    password = PasswordField('Password', validators=[validators.InputRequired()])


class VerifyForm(FlaskForm):
    """Form used to verify SMS codes"""
    verification_code = StringField(
        'Verification code',
        validators=[
            validators.InputRequired(),
            validators.Length(min=4, max=10)
        ]
    )

class PaymentForm(FlaskForm):
    """Form used to submit payments"""
    send_to = SelectField(
        'Send to', 
        choices=[
            ('neville@hogwarts.ac.uk', 'Neville L. <neville@hogwarts.ac.uk>'), 
            ('hermione@hogwarts.ac.uk', 'Hermione G. <hermione@hogwarts.ac.uk>'), 
            ('harry@hogwarts.ac.uk', 'Harry P. <harry@hogwarts.ac.uk>'), 
            ('ron@hogwarts.ac.uk', 'Ron W. <ron@hogwarts.ac.uk>'), 
            ('luna@hogwarts.ac.uk', 'Luna L. <luna@hogwarts.ac.uk>')],
        validators=[validators.InputRequired()])
    amount = IntegerField('Amount', validators=[validators.InputRequired()])