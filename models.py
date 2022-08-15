import random
from exts import db
from utils.others import user_img_lst
import time


class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(30), nullable=False, unique=True, index=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), nullable=True,
                       default=lambda: user_img_lst[random.randint(0, len(user_img_lst) - 1)])
    tags = db.Column(db.String(100), default='[]')
    role = db.Column(db.Integer, default=1)
    forbid = db.Column(db.Integer, default=lambda: int(time.time()))
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


class TopicModel(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.String(50), nullable=False)
    topic_content = db.Column(db.String(200), nullable=False)
    op1 = db.Column(db.String(50))
    op2 = db.Column(db.String(50))
    op3 = db.Column(db.String(50))
    op4 = db.Column(db.String(50))


class VoteModel(db.Model):
    __tablename__ = 'vote'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(30), nullable=False)
    op = db.Column(db.SmallInteger, nullable=False)


class RoomModel(db.Model):
    __tablename__ = 'room'
    room_id = db.Column(db.String(100), primary_key=True)
    user1_id = db.Column(db.String(30), nullable=False)
    user2_id = db.Column(db.String(30), nullable=False)


class ChatMapModel(db.Model):
    __tablename__ = 'chat_map'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(30), nullable=False, unique=True, index=True)
    user_sid = db.Column(db.String(50), nullable=False)


class MessageModel(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.String(100))
    sender_id = db.Column(db.String(30), nullable=False)
    reader_id = db.Column(db.String(30), nullable=False)
    read = db.Column(db.Boolean, default=False)
    info = db.Column(db.Text)


class JobsModel(db.Model):
    __tablename__ = 'jobs_detail'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job = db.Column(db.String(20))
    city = db.Column(db.String(15))
    salary = db.Column(db.String(15))
    education = db.Column(db.String(10))
    experience = db.Column(db.String(10))
    goodList = db.Column(db.Text)
    needList = db.Column(db.Text)
    jobInfo = db.Column(db.Text)
    company = db.Column(db.String(20))
    companyType = db.Column(db.String(15))
    companyPeople = db.Column(db.String(15))
    companyPosition = db.Column(db.Text)
    companyInfo = db.Column(db.Text)

