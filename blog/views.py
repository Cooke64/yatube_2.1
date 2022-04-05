from flask import render_template, flash, url_for, redirect, abort, request
from flask_login import login_required, current_user

from app import app, db, mail, Post, Comment, Like, User
from forms import (
    PostCreateForm, AddCommentForm,
    EditCommentForm, ContactUsForm
)
from utils.utils import send_message


@app.route('/')
def get_index_page():
    """Главная страница сайта. Отображение всех постов."""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(
        Post.created_at.desc()).paginate(page=page, per_page=3)
    try:
        last_post = Post.query.all()[-1]
    except:
        last_post = None
    users = User.query.all()
    return render_template(
        'blog/index.html',
        last_post=last_post,
        posts=posts,
        users=users,
    )


@app.route('/search')
def search_query():
    """Отображение результатов поиска по указанному запросу."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q')
    if q:
        posts = Post.query.filter(
            Post.title.contains(q) | Post.text.contains(q)).paginate(
            page=page, per_page=3)
        return render_template(
            'blog/search_result.html',
            posts=posts,
            q=q
        )


@app.route('/about')
def get_about_page():
    """Страничка о создателе блога."""
    return render_template('blog/about.html', )


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_new_post():
    """Создание нового поста в ленту пользователем."""
    form = PostCreateForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            text=form.text.data,
            author=current_user,
        )
        db.session.add(post)
        db.session.commit()
        flash('Пост добавлен', 'success')
        return redirect(url_for('index'))
    return render_template('blog/create.html', form=form)


@app.route('/post/edit/<post_id>', methods=['GET', 'POST'])
@login_required
def post_edit(post_id: int):
    """Изменение поста."""
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostCreateForm()
    if form.validate_on_submit():
        post.title = request.form['title']
        post.text = request.form['text']
        try:
            db.session.commit()
            return redirect(url_for('post_detail', post_id=post.id))
        except Exception as error:
            return error
    elif request.method == 'GET':
        form.title.data = post.title
        form.text.data = post.text
    # Передается в шаблон для переключения при рендере шаблона создать/изменить пост
    is_edit = True
    return render_template('blog/create.html', is_edit=is_edit, post=post,
                           form=form)


@app.route('/post/delete/<post_id>', methods=['GET', 'POST'])
@login_required
def post_delete(post_id: int):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Пост удален:(', 'danger')
        return redirect(url_for('index'))
    except Exception as error:
        return error


@app.route("/post/<post_id>", methods=["GET", "POST"])
def get_post_detail(post_id: int):
    """Отображение конкретного поста с возможностью добавления комментария и
    поставить отметку нравится/не нравится.
    """
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id)
    if current_user.is_authenticated:
        like = Like.query.filter_by(
            author=current_user.id,
            post_id=post_id).first()
    else:
        like = False
    form = AddCommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            text=form.text.data,
            post_id=post.id,
            user_id=current_user.id,
        )
        db.session.add(comment)
        db.session.commit()
        flash("Комментарий добавлен.", "success")
        return redirect(url_for("post_detail", post_id=post.id))
    return render_template("blog/post_detail.html", post=post, like=like,
                           form=form, comments=comments)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html'), 404


@app.errorhandler(403)
def internal_error(error):
    db.session.rollback()
    return render_template('error/500.html'), 403


@app.route("/comment/<comm_id>/", methods=["GET", "POST"])
@login_required
def comment_edit(comm_id: int):
    comment = Comment.query.get_or_404(comm_id)
    if comment.author != current_user and not current_user.is_authenticated:
        abort(403)
    form = EditCommentForm()
    if form.validate_on_submit() and request.method == 'GET':
        comment.text = request.form['text']
        try:
            db.session.commit()
            return redirect(url_for('post_detail', post_id=comment.post.id))
        except Exception as error:
            return error
    else:
        form.text.data = comment.text
    return render_template('blog/comment_edit.html', form=form)


@app.route('/contact_us', methods=["GET", "POST"])
@login_required
def contact_us():
    form = ContactUsForm()
    if form.validate_on_submit():
        # Если форма валидна, то вызывается функция отправить сообщение
        send_message(form)
    return render_template('blog/contact_us.html', form=form)


@app.route('/like_post/<post_id>', methods=["GET", "POST"])
@login_required
def like_post(post_id: int):
    """Поставить/убрать отметку лайк посту."""
    post = Post.query.filter_by(id=post_id)
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()
    if not post:
        flash('error', 'warning')
    elif like:
        # Если есть лайк к текущему посту, он удаляется из бд.
        db.session.delete(like)
        db.session.commit()
    else:
        # Если лайка нет к текущему посту, он добавляется в бд.
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
    return redirect(url_for('post_detail', post_id=post_id))
