from flask import Blueprint
from .forbid import ForbidAPI

__all__ = [
    'admin_bp'
]


def bp_init():
    bp = Blueprint('admin', __name__, url_prefix='/admin')
    bp.add_url_rule('/forbid/', view_func=ForbidAPI.as_view('forbid'), methods=['PUT'])
    return bp


admin_bp = bp_init()
