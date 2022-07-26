from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
import jwt
from jwt import exceptions
import time
from .others import rand_str
from .log import Log
from exts import db
from models import UserModel


def create_token(user: UserModel, refresh_token: bool = False) -> str:
    headers: dict = {
        "alg": "HS256",
        "typ": "JWT",
    }
    exp: int = int(time.time() + 600) if refresh_token is False else int(time.time() + 3600 * 24 * 14)
    payload: dict = {
        "name": user.username,
        "user_id": user.user_id,
        "exp": exp,
        "iss": 'byszqq'
    }
    key: str = current_app.config.get('JWT_SECRET_KEY')
    if refresh_token is True:
        u = UserModel.query.filter(UserModel.user_id == user.user_id).first()
        refresh_key = rand_str(6)
        u.refresh_key = refresh_key
        payload['refresh_key'] = refresh_key
        db.session.commit()
    token: str = jwt.encode(payload=payload, key=key, algorithm='HS256', headers=headers)
    return token


def validate_token(token: str, refresh_token: bool = False) -> tuple[dict, str]:
    payload: [dict, None] = None
    msg: [str, None] = None
    key: str = current_app.config.get('JWT_SECRET_KEY')
    try:
        payload = jwt.decode(jwt=token, key=key, algorithms=['HS256'], issuer='byszqq')
        if refresh_token is True:
            try:
                user = UserModel.query.filter(UserModel.user_id == payload.get('user_id')).first()
            except SQLAlchemyError as e:
                Log.error(e)
                return dict(), 'database error'
            else:
                if user.refresh_key != payload.get('refresh_key'):
                    msg = 'refresh key 错误'
        else:
            if payload.get('refresh_key') is not None:
                msg = '禁止用refresh token'
    except exceptions.ExpiredSignatureError:
        msg = 'token已失效'
    except jwt.DecodeError:
        msg = 'token认证失败'
    except jwt.InvalidTokenError:
        msg = '非法的token'
    return payload, msg
