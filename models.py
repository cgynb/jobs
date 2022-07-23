import random
from exts import db
from utils.others import user_img_lst


class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(30), nullable=False, unique=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), nullable=True, default=lambda: user_img_lst[random.randint(0, len(user_img_lst)-1)])
    tags = db.Column(db.String(100))
    refresh_key = db.Column(db.String(20))


class CaptchaModel(db.Model):
    __tablename__ = 'captcha'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    captcha = db.Column(db.String(10), nullable=False)


class LikeModel(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(30), db.ForeignKey("user.user_id"), nullable=False)


class CollectModel(db.Model):
    __tablename__ = 'collect'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(30), db.ForeignKey("user.user_id"), nullable=False)
