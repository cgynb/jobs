from flask import Blueprint

from .answer import AnswerAPI
from .question import QuestionAPI
from .photo import PhotoAPI
from .vote import VoteAPI

__all__ = [
    'forum_bp'
]


def bp_init() -> Blueprint:
    bp = Blueprint('forum', __name__, url_prefix='/forum')
    bp.add_url_rule('/vote/', view_func=VoteAPI.as_view('vote'))
    bp.add_url_rule('/photo/', view_func=PhotoAPI.as_view('photo'))
    bp.add_url_rule('/answer/', view_func=AnswerAPI.as_view('answer'))
    bp.add_url_rule('/question/', view_func=QuestionAPI.as_view('question'))
    return bp


forum_bp = bp_init()
