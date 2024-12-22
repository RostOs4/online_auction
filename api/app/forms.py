# Определение форм

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Электронная почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтверждение пароля', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class EditAccountForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=1, max=150)])
    email = EmailField('Электронная почта', validators=[DataRequired(), Email()])
    first_name = StringField('Имя', validators=[Length(max=150)])
    last_name = StringField('Фамилия', validators=[Length(max=150)])
    phone_number = StringField('Номер телефона', validators=[Length(max=15)])
    address = StringField('Адрес', validators=[Length(max=255)])
    submit = SubmitField('Сохранить изменения')

