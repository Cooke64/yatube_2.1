from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import (
    DataRequired, Length,
    Email, EqualTo,
    ValidationError,
    InputRequired
)

from app import User


class RegistrationForm(FlaskForm):
    """ Форма для регистрации новых пользователей."""
    username = StringField('Имя пользователя',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   Length(min=2, max=20)])
    confirm_password = PasswordField('Подтвердите пароль',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Такое имя уже занято. Выбери другое')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Такой email уже занят. Выбери другой')


class LoginForm(FlaskForm):
    """Форма для входа на сайт зарегистрированным пользователям."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить')


class ProfileForm(FlaskForm):
    """Форма для изменения данных профиля."""
    username = StringField(
        'Имя пользователя', validators=[Length(min=3, max=20)]
    )
    email = StringField('Email', validators=[Email()])
    picture = FileField(
        'Сменить фотографию профиля',
        validators=[FileAllowed(['jpg', 'png', 'jpeg'])]
    )

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Такое имя уже занято. Выбери другое')

    def validate_email(self, email):
        if email.data != current_user.username:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Такой email уже занят. Выбери другой')


class PostCreateForm(FlaskForm):
    """Форма для создания нового поста."""
    title = StringField(
        'Заголовок', validators=[DataRequired()]
    )
    text = TextAreaField(
        'Содержание поста', validators=[DataRequired()]
    )


class AddCommentForm(FlaskForm):
    """Форма для добавления комментария."""
    body = TextAreaField("Текст комментария", validators=[InputRequired()])


class EditCommentForm(FlaskForm):
    """Форма для изменения комментария."""
    body = TextAreaField("Текст комментария", validators=[InputRequired()])


class ChangeDataForm(FlaskForm):
    """Форма для изменения персональных данных."""
    age = StringField('Возраст', )
    country = StringField('Страна', )
    city = StringField('Город', )
    telegram = StringField('Телеграм', )
    git = StringField('Мой github', )


class RequestResetForm(FlaskForm):
    """Форма для заполнения email при смене пароля."""
    email = StringField('Email',
                        validators=[DataRequired()])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Такого пользователя не существует:/')


class ResetPassForm(FlaskForm):
    """Форма для изменения пароля на новый."""
    password = PasswordField(
        'Новый пароль', validators=[DataRequired(), Length(min=2, max=20)]
    )
    confirm_password = PasswordField(
        'Подтвердить пароль', validators=[DataRequired(), EqualTo('password')]
    )


class ContactUsForm(FlaskForm):
    """Форма обратной связи."""
    message = TextAreaField(
        'Оставьте ваш отзыв', validators=[DataRequired()]
    )


class SendMessageForm(FlaskForm):
    """Форма отправки сообщений"""
    body = TextAreaField(
        'Отправьте ваше сообщение', validators=[Length(max=199)]
    )
