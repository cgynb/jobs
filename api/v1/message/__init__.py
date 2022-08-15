from flask import Blueprint
from .message import MessageAPI
from .room import RoomAPI

__all__ = [
    'message_bp'
]


def bp_init() -> Blueprint:
    bp = Blueprint('message', __name__, url_prefix='/message')
    bp.add_url_rule('/', view_func=MessageAPI.as_view('message'))
    bp.add_url_rule('/room/', view_func=RoomAPI.as_view('room'))
    return bp


message_bp = bp_init()
