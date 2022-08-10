import typing as t
from flask import g, jsonify, Response
from functools import wraps
import time


class Limiter:
    ROLES = {
        'user': {
            'code': [1],
            'message': 'login required',
            'validate_func': lambda user, roles: user.role in roles
        },
        'admin': {
            'code': [2],
            'message': 'admin required',
            'validate_func': lambda user, roles: user.role in roles
        },
        'speaker': {
            'code': [1, 2],
            'message': 'you have been forbidden',
            'validate_func': lambda user, roles: user.role in roles and user.forbid < time.time()
        }
    }

    def __init__(self, role='user'):
        self.role = self.ROLES.get(role) if self.ROLES.get(role) is not None else self.ROLES.get('user')
        self.validate_func = self.role.get('validate_func')

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if hasattr(g, 'user'):
                if self.validate_func(g.user, self.role.get('code')):
                    return func(*args, **kwargs)
                else:
                    return jsonify({'code': 403, 'message': self.role.get('message')})
            else:
                return jsonify({'code': 403, 'message': 'login required'})
        return wrapper


