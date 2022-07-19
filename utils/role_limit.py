from flask import g, jsonify
from functools import wraps


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if hasattr(g, 'user'):
            return func(*args, **kwargs)
        return jsonify({'code': 403, 'message': "login required"})
    return wrapper

