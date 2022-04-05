from flask import flash, url_for, redirect
from flask_login import login_required, current_user

from app import app, db, User


@app.route('/follow/<username>')
@login_required
def follow_user(username):
    """Добавление автора постов в избранные."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'Автор с именем {username} не найден')
        return redirect(url_for('index'))
    if user == current_user:
        flash('У нас нельзя подписаться на самого себя!')
        return redirect(url_for('user_profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'Вы подписались на {username}!')
    return redirect(url_for('user_profile', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow_user(username):
    """Удаление автора из избранных авторов."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f'Автор с именем {username} не найден')
        return redirect(url_for('index'))
    if user == current_user:
        flash('Нельзя отписаться от самого себя, вы чего??')
        return redirect(url_for('user_profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'ы больше не подписаны на {username} :(')
    return redirect(url_for('user_profile', username=username))
