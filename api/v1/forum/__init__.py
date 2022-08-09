from flask import Blueprint

from .answer import AnswerAPI
from .question import QuestionAPI

__all__ = [
    'forum_bp'
]


def bp_init() -> Blueprint:
    bp = Blueprint('forum', __name__, url_prefix='/forum')
    bp.add_url_rule('/question/', view_func=QuestionAPI.as_view('question'))
    bp.add_url_rule('/answer/', view_func=AnswerAPI.as_view('answer'))
    return bp


forum_bp = bp_init()
