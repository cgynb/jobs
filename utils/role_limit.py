import typing as t
from flask import g, jsonify, Response
from functools import wraps


def login_required(func: t.Callable) -> t.Callable:
    @wraps(func)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Union[t.Callable, Response]:
        if hasattr(g, 'user'):
            return func(*args, **kwargs)
        return jsonify({'code': 403, 'message': "login required"})
    return wrapper

