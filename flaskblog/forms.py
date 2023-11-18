from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
import regex


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired() ], id = "ent_passw")
    show_entered_password = BooleanField('Show  ', id='ent_pass')
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired(), EqualTo('password')], id = "con_passw")
    show_confirm_password = BooleanField('Show  ', id='con_pass')
    submit = SubmitField('Sign Up')

   




    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
  
    flag= 0
    def validate_password(self, password):
        while True:
            if (len(password.data)<=8):
                    flag = -1
                    break
                    
            elif not regex.search("[a-z]", password.data):
                    flag = -1
                    break
                    
            elif not regex.search("[A-Z]", password.data):
                    flag = -1
                    break

            elif not regex.search("[0-9]", password.data):
                    flag = -1
                    break

            elif not regex.search("[_@$]" , password.data):
                    flag = -1
                    break

            elif regex.search("\s" , password.data):
                    flag = -1
                    break

            else:
                    flag = 0
                    break
                    
                
        
        if flag == -1:
            raise ValidationError("Password must satisfy above conditions ")
                

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()],id='password')
    show_password = BooleanField('Show password', id='check')
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    file_path = FileField('File', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'pdf'], 'Invalid file format')])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')
       
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class InviteUserForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Send Mail')


class NewCommentForm(FlaskForm):
    new_comment = StringField('Comment something!', validators=[DataRequired()])
    submit = SubmitField("Edit Comment")


