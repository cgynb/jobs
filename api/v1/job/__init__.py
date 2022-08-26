from flask import Blueprint

from .library import LibraryAPI

__all__ = [
    'job_bp'
]


def bp_init():
    bp = Blueprint('job', __name__, url_prefix='/job')
    bp.add_url_rule('/library/', view_func=LibraryAPI.as_view('library'))
    return bp


job_bp = bp_init()
