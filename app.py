from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail
from datetime import datetime
from flask_login import UserMixin
import itsdangerous


from config import Config

app = Flask(__name__)
app._static_folder = 'static'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676df2de280ba245'
app.config.from_object(Config)
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
mail = Mail(app)


migrate = Migrate(app, db)
csrf = CSRFProtect(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('user.id'))
                     )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    image_file = db.Column(db.String(), nullable=True, default='default.jpg')
    password = db.Column(db.String(59), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # Персональные данные, необязательные, для профиля
    age = db.Column(db.Integer,
                    default='Не заполнено.', nullable=True)
    country = db.Column(db.String(59),
                        default='Не заполнено.', nullable=True)
    city = db.Column(db.String(59),
                     default='Не заполнено.', nullable=True)
    telegram = db.Column(db.String(59),
                         default='Не заполнено.', nullable=True)
    git = db.Column(db.String(199), nullable=True)
    # Подписчики
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref='Подписчики',
        lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy=True)

    def __repr__(self):
        return f'{self.username} has {self.email}'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def get_reset_token(self):
        auth_s = itsdangerous.Serializer(app.config['SECRET_KEY'])
        return auth_s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        auth_s = itsdangerous.Serializer(app.config['SECRET_KEY'])
        try:
            user_id = auth_s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )
    comments = db.relationship('Comment', backref='posts', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)

    def __repr__(self):
        return f"Post '{self.title}', created '{self.created_at}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return self.body


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)
