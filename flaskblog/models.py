from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

user_categories = db.Table(
    'user_categories',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_connected = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', foreign_keys=[user_id], backref='friendships')
    friend = db.relationship('User', foreign_keys=[friend_id])

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', cascade='all, delete', lazy=True)
    comments = db.relationship('Comment', backref='author', cascade='all, delete', lazy=True)
    friendship = db.relationship(
        'Friendship',
        primaryjoin="(User.id == Friendship.user_id) | (User.id == Friendship.friend_id)",
        backref='users',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    categories = db.relationship('Category', secondary='user_categories', cascade='all, delete', back_populates='users')
    likes = db.relationship('Like', backref='user', cascade='all, delete', lazy=True)

    def add_friend(self, user):
        if not self.is_friends_with(user):
            friendship1 = Friendship(user_id=self.id, friend_id=user.id)
            friendship2 = Friendship(user_id=user.id, friend_id=self.id)
            
            db.session.add_all([friendship1, friendship2])
            db.session.commit()
    def is_friends_with(self, user):
        return Friendship.query.filter(
            (Friendship.user_id == self.id) & (Friendship.friend_id == user.id)
            | (Friendship.user_id == user.id) & (Friendship.friend_id == self.id)
        ).count() > 0

    @property
    def friends(self):
        return User.query.join(Friendship, (Friendship.friend_id == User.id)).filter(Friendship.user_id == self.id)
    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'], 1800)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{ self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    comments = db.relationship('Comment', backref='post', cascade='all, delete', lazy=True)
    likes = db.relationship('Like', backref='post', cascade='all, delete', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}f', '{self.date_posted}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    users = db.relationship(
        'User',
        secondary=user_categories,
        back_populates='categories'
    )

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
