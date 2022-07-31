from flask import Blueprint
from .question import bp as question_bp
from .answer import bp as answer_bp
from .answer import AnswerAPI
from .question import QuestionAPI

__all__ = [
    'forum_bp'
]


def bp_init():
    bp = Blueprint('forum', __name__, url_prefix='/forum')
    question_bp.add_url_rule('/', view_func=QuestionAPI.as_view(''))
    answer_bp.add_url_rule('/', view_func=AnswerAPI.as_view(''))
    bp.register_blueprint(answer_bp)
    bp.register_blueprint(question_bp)
    return bp


forum_bp = bp_init()
