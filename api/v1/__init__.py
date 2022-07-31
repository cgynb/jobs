from flask import Blueprint

from .user import bp as user_bp
from .article import article_bp
from .admin import bp as admin_bp
from .forum import forum_bp
from .user import UserAPI, CaptchaAPI, LoginAPI, RefreshAPI


__all__ = [
    'v1_bp'
]


def bp_init():
    bp = Blueprint('v1', __name__, url_prefix='/v1')

    user_bp.add_url_rule('/login/', view_func=LoginAPI.as_view('login'), methods=['POST'])
    user_bp.add_url_rule('/refresh/', view_func=RefreshAPI.as_view('refresh'), methods=['POST'])
    user_bp.add_url_rule('/captcha/', view_func=CaptchaAPI.as_view('captcha'), methods=['GET', 'POST'])
    user_bp.add_url_rule('/', view_func=UserAPI.as_view('user'), methods=['POST', 'PUT'])

    bp.register_blueprint(user_bp)
    bp.register_blueprint(article_bp)
    bp.register_blueprint(forum_bp)
    bp.register_blueprint(admin_bp)

    return bp


v1_bp = bp_init()

