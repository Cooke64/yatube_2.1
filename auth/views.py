from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from app import app, db, mail, User, bcrypt
from forms import RegistrationForm, LoginForm, RequestResetForm, ResetPassForm
from utils.utils import send_reset_email, make_hashed_password

@app.before_request
def get_last_seen_before_request():
    """Отображение последнего визита пользователя."""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/login', methods=['POST', 'GET'])
def make_login_user():
    """Авторизация пользователя."""
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password,
                form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(
                url_for('index'))
        else:
            flash('Проверьте email', 'danger')
    return render_template('auth/login.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def make_register_user():
    """Авторизация пользователя."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = make_hashed_password(form)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('регистрация прошла успешно. Можете войти на сайт', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Страница для отображения формы смены пароля.
    При валидации данных отправляется письмо на email.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('На Вашу почту отправлено сообщение', 'warning')
        return redirect(url_for('login'))
    return render_template(
        'auth/reset_pass.html',
        form=form,
    )


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_process(token):
    """При получении ссылки при смене пароля, пользователь получает хешированную ссылку,
     которая будет проверять и при верификации тот может сменить пароль.
     """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Введите заново email. Произошла ошибка', 'warning')
        return redirect(url_for('reset_password_request'))
    form = ResetPassForm()
    if form.validate_on_submit():
        hashed_password = make_hashed_password(form)
        user.password = hashed_password
        db.session.commit()
        flash('Пароль изменен. Можете войти на сайт', 'success')
        return redirect(url_for('login'))
    is_reset = True
    return render_template(
        'auth/reset_pass.html',
        form=form,
        is_reset=is_reset,
    )
