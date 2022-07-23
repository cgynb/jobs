from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import jwt
from jwt import exceptions
import time
from .others import rand_str
from exts import db
from models import UserModel


def create_token(user, refresh_token=False):
    headers = {
        "alg": "HS256",
        "typ": "JWT",
    }
    exp = int(time.time() + 600) if refresh_token is False else int(time.time() + 3600 * 24 * 14)
    payload = {
        "name": user.username,
        "user_id": user.user_id,
        "exp": exp,
        "iss": 'byszqq'
    }
    key = current_app.config.get('JWT_SECRET_KEY')
    if refresh_token is True:
        u = UserModel.query.filter(UserModel.user_id == user.user_id).first()
        refresh_key = rand_str(6)
        u.refresh_key = refresh_key
        payload['refresh_key'] = refresh_key
        db.session.commit()
    token = jwt.encode(payload=payload, key=key, algorithm='HS256', headers=headers)
    return token


def validate_token(token, refresh_token=False):
    payload = None
    msg = None
    key = current_app.config.get('JWT_SECRET_KEY')
    try:
        payload = jwt.decode(jwt=token, key=key, algorithms=['HS256'], issuer='byszqq')
        if refresh_token is True:
            user = UserModel.query.filter(UserModel.user_id == payload.get('user_id')).first()
            print(payload.get('refresh_key'))
            if user.refresh_key != payload.get('refresh_key'):
                msg = 'refresh key 错误'
    except exceptions.ExpiredSignatureError:
        msg = 'token已失效'
    except jwt.DecodeError:
        msg = 'token认证失败'
    except jwt.InvalidTokenError:
        msg = '非法的token'
    return payload, msg

