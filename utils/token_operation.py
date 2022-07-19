# -*- coding: utf-8 -*-
# @Time    : 2022/5/6 11:50
# @Author  : CGY
# @File    : token_operation.py
# @Project : NewWaiMai 
# @Comment : token
from flask import current_app
import jwt
from jwt import exceptions
import time


def create_token(user, refresh_token=False):
    headers = {
        "alg": "HS256",
        "typ": "JWT",
    }
    exp = int(time.time() + 3600) if refresh_token is False else int(time.time() + 3600 * 24 * 14)
    payload = {
        "name": user.username,
        "user_id": user.user_id,
        "exp": exp,
        "iss": 'sbb'
    }
    token = jwt.encode(payload=payload, key=current_app.config.get('JWT_SECRET_KEY'), algorithm='HS256',
                       headers=headers)
    return token


def validate_token(token):
    payload = None
    msg = None
    try:
        payload = jwt.decode(jwt=token, key=current_app.config.get('JWT_SECRET_KEY'), algorithms=['HS256'], issuer='sbb')
    except exceptions.ExpiredSignatureError:
        msg = 'token已失效'
    except jwt.DecodeError:
        msg = 'token认证失败'
    except jwt.InvalidTokenError:
        msg = '非法的token'
    return payload, msg

