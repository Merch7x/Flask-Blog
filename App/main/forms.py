from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, PasswordField, \
    BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, \
    DataRequired, Email, EqualTo, Length
from App.models import User


class EditProfileForm(FlaskForm):
    """Enables a users profile to be set and edited"""
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[
                             Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

     # prevent duplicate usernames
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username'))


class PostForm(FlaskForm):
    post = TextAreaField(_l("What's on your mind?"), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))
