from flask import Blueprint

from .user import user_bp
from .article import article_bp
from .admin import admin_bp
from .forum import forum_bp
from .message import message_bp


__all__ = [
    'v1_bp'
]


def bp_init():
    bp = Blueprint('v1', __name__, url_prefix='/v1')

    bp.register_blueprint(user_bp)
    bp.register_blueprint(article_bp)
    bp.register_blueprint(forum_bp)
    bp.register_blueprint(admin_bp)
    bp.register_blueprint(message_bp)

    return bp


v1_bp = bp_init()

