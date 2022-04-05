import os
import secrets

from flask import flash, url_for, redirect, abort
from flask_login import login_required, current_user
from flask_mail import Message
from PIL import Image

from app import app, db, mail, Post, Comment, Like, User, bcrypt


def save_pic(form_pic):
    """Сохраняет изображение."""
    random = secrets.token_hex(10)
    _, file_extention = os.path.splitext(form_pic.filename)
    pic_file_name = random + file_extention
    pic_path = os.path.join(
        app.root_path, 'static/profile_pics', pic_file_name)
    # Сохраняем фото в определенном размере
    pic_size = (400, 400)
    image = Image.open(form_pic)
    image.thumbnail(pic_size)
    image.save(pic_path)
    return pic_file_name


def send_message(form):
    """Отправляет администратору сайта письмо, в котором содержится отзыв."""
    if not current_user.is_authenticated:
        abort(403)
    author = current_user.username
    message = form.message.data
    msg = Message(f'Отзыв пользователя {author}',
                  recipients=['pozdeev1994@mail.ru'])
    msg.body = message
    mail.send(msg)
    flash('Сообщение отправлено', 'success')
    return redirect(url_for('index'))


def send_reset_email(user):
    """Отправляет на почту пользователя письмо со ссылкой,
     по которой тот должен перейти и поменять пароль.
     """
    token = user.get_reset_token()
    msg = Message('Смена пароля',
                  recipients=[user.email])
    msg.body = f'''
    Чтобы поменять пароль,перейдите по ссылке:
    {url_for('reset_token', token=token, _external=True)}
    Если вы не получали этого сообщения,просто проигнорируйте данное сообщение.
    '''
    mail.send(msg)


def make_hashed_password(form):
    hashed_password = bcrypt.generate_password_hash(
        form.password.data).decode('utf-8')
    return hashed_password
