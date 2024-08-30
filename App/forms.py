from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, \
    BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, \
    DataRequired, Email, EqualTo, Length
from App.models import User


class LoginForm(FlaskForm):
    """User Login Form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    """User Registration Form"""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[
                        DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # custom validators for form fields
    def validate_username(self, username):
        """Validate username is unique"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username is taken!')

    def validate_email(self, email):
        """Validate email is unique"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already exists!')


class EditProfileForm(FlaskForm):
    """Enables a users profile to be set ad edited"""
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField("What's on your mind?", validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
