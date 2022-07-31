from flask import Blueprint

from .article import bp as a_bp
from .article import ArticleAPI
from .comment import bp as comment_bp
from .comment import CommentAPI
from .recommend import bp as recommend_bp
from .recommend import RecommendAPI
from .lc import bp as lc_bp
from .lc import LCAPI

__all__ = [
    'article_bp'
]


def bp_init():
    bp = Blueprint('article', __name__, url_prefix='/article')
    a_bp.add_url_rule('/', view_func=ArticleAPI.as_view(''), methods=['GET'])
    lc_bp.add_url_rule('/', view_func=LCAPI.as_view(''), methods=['GET', 'PUT'])
    comment_bp.add_url_rule('/', view_func=CommentAPI.as_view(''), methods=['POST'])
    recommend_bp.add_url_rule('/', view_func=RecommendAPI.as_view(''), methods=['GET'])
    bp.register_blueprint(a_bp)
    bp.register_blueprint(comment_bp)
    bp.register_blueprint(recommend_bp)
    bp.register_blueprint(lc_bp)
    return bp


article_bp = bp_init()
