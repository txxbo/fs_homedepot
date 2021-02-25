from flask_wtf import FlaskForm
from scraper.models import User
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, URL, DataRequired


class ProductForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Add')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[])
    password2 = PasswordField(
        'Repeat Password', validators=[EqualTo('password')])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username and len(username.data) > 3:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
