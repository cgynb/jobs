from flask import Blueprint

from .user import bp as user_bp
from .article import bp as article_bp
from .admin import bp as admin_bp
from .forum import bp as forum_bp
from .user import UserAPI, CaptchaAPI, LoginAPI, RefreshAPI
from .article import ArticleAPI, CommentAPI, RecommendAPI, LCAPI
from .forum import QuestionAPI, AnswerAPI


__all__ = [
    'v1_bp'
]


def bp_init():
    bp = Blueprint('v1', __name__, url_prefix='/v1')

    user_bp.add_url_rule('/login/', view_func=LoginAPI.as_view('login'), methods=['POST'])
    user_bp.add_url_rule('/refresh/', view_func=RefreshAPI.as_view('refresh'), methods=['POST'])
    user_bp.add_url_rule('/captcha/', view_func=CaptchaAPI.as_view('captcha'), methods=['GET', 'POST'])
    user_bp.add_url_rule('/', view_func=UserAPI.as_view('user'), methods=['POST', 'PUT'])

    article_bp.add_url_rule('/', view_func=ArticleAPI.as_view('article'), methods=['GET'])
    article_bp.add_url_rule('/lc/', view_func=LCAPI.as_view('like-collect'), methods=['GET', 'PUT'])
    article_bp.add_url_rule('/comment/', view_func=CommentAPI.as_view('comment'), methods=['POST'])
    article_bp.add_url_rule('/recommend/', view_func=RecommendAPI.as_view('recommend'), methods=['GET'])

    forum_bp.add_url_rule('/question/', view_func=QuestionAPI.as_view('question'))
    forum_bp.add_url_rule('/answer/', view_func=AnswerAPI.as_view('answer'))

    bp.register_blueprint(user_bp)
    bp.register_blueprint(article_bp)
    bp.register_blueprint(forum_bp)

    return bp


v1_bp = bp_init()

