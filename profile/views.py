from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required

from app import app, db, User, Post, Message
from forms import ProfileForm, ChangeDataForm, SendMessageForm
from utils.utils import save_pic


@app.route('/profile_edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    user = User.query.filter_by(username=current_user.username).first_or_404()
    follow = user.followed.count()
    form = ProfileForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.picture.data:
                pic_file = save_pic(form.picture.data)
                current_user.image_file = pic_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Профиль успешно изменен.', 'success')
            return redirect(url_for('user_profile', username=current_user.username))
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static',
        filename='profile_pics/' + current_user.image_file
    )
    is_edit = True
    return render_template(
        'profile/profile.html',
        image_file=image_file,
        follow=follow,
        form=form,
        is_edit=is_edit,
        user=user,
    )


@app.route('/profile/<string:username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    follow = user.followed.count()
    image_file = url_for(
        'static',
        filename='profile_pics/' + user.image_file
    )
    return render_template(
        'profile/profile.html',
        image_file=image_file,
        user=user,
        follow=follow,
    )


@app.route('/profile/change_data', methods=['GET', 'POST'])
@login_required
def change_data():
    form = ChangeDataForm()
    if form.validate_on_submit():
        current_user.age = form.age.data
        current_user.country = form.country.data
        current_user.city = form.city.data
        current_user.telegram = form.telegram.data
        current_user.git = form.git.data
        db.session.commit()
        flash('Профиль успешно изменен.', 'success')
        return redirect(
            url_for('user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.age.data = current_user.age
        form.country.data = current_user.country
        form.city.data = current_user.city
        form.telegram.data = current_user.telegram
        current_user.git = form.git.data
        return render_template(
            'profile/change_data.html',
            form=form,
        )


@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(
        Post.created_at.desc()).paginate(page=page, per_page=3)
    return render_template(
        'profile/user_posts.html',
        user=user,
        posts=posts)


@app.route('/profile/<string:username>/followers')
def user_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template(
        'profile/user_followers.html',
        user=user,
    )


@app.route('/profile/<string:username>/comments')
def user_comments(username):
    user = User.query.filter_by(username=username).first_or_404()
    follow = user.followed
    return render_template(
        'profile/user_comments.html',
        user=user,
        follow=follow
    )


@app.route('/profile/<string:username>/likes')
def user_likes(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template(
        'profile/user_likes.html',
        user=user,
    )


@app.route('/profile/<string:username>/send_message')
@login_required
def send_message(username):
    form = SendMessageForm()
    if form.validate_on_submit():
        message = Message(
            body=form.body.data,
            sender=current_user.username,
            getter=username,
        )
        db.session.add(message)
        db.session.commit()
        flash('Ваше сообщение отправлено', 'success')
        return redirect(url_for(f'/profile/{username}'))
    return render_template('profile/send_message.html', form=form)


@app.route('/profile/all_messages')
@login_required
def all_messages():
    user = current_user
    messages_sent = Message.query.filter_by(getter=user).all()
    messages_got = Message.query.filter_by(sender=user).all()
    return render_template(
        'profile/all_messages.html',
        user=user,
        messages_sent=messages_sent,
        messages_got=messages_got,
    )
