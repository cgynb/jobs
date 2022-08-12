from flask import Blueprint

from .user import UserAPI
from .captcha import CaptchaAPI
from .login import LoginAPI
from .refresh import RefreshAPI

__all__ = [
    'user_bp'
]


def bp_init():
    bp = Blueprint('user', __name__, url_prefix='/user')
    bp.add_url_rule('/login/', view_func=LoginAPI.as_view('login'), methods=['POST'])
    bp.add_url_rule('/refresh/', view_func=RefreshAPI.as_view('refresh'), methods=['POST'])
    bp.add_url_rule('/captcha/', view_func=CaptchaAPI.as_view('captcha'), methods=['GET', 'POST'])
    bp.add_url_rule('/', view_func=UserAPI.as_view('user'), methods=['GET', 'POST', 'PUT'])
    return bp


user_bp = bp_init()
