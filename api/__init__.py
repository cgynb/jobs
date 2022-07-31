from flask import Blueprint
from .v1 import v1_bp

__all__ = [
    'api_bp'
]


def bp_init():
    bp = Blueprint('api', __name__, url_prefix='/api')
    bp.register_blueprint(v1_bp)
    return bp


api_bp = bp_init()
