from flask import Blueprint

from .article import ArticleAPI
from .comment import CommentAPI
from .recommend import RecommendAPI
from .lc import LCAPI

__all__ = [
    'article_bp'
]


def bp_init():
    bp = Blueprint('article', __name__, url_prefix='/article')
    bp.add_url_rule('/', view_func=ArticleAPI.as_view(''), methods=['GET'])
    bp.add_url_rule('/lc/', view_func=LCAPI.as_view('lc'), methods=['GET', 'PUT'])
    bp.add_url_rule('/comment/', view_func=CommentAPI.as_view('comment'), methods=['POST'])
    bp.add_url_rule('/recommend/', view_func=RecommendAPI.as_view('recommend'), methods=['GET'])
    return bp


article_bp = bp_init()
