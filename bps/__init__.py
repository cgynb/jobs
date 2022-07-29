from .user import bp as user_bp
from .article import bp as article_bp
from .admin import bp as admin_bp
from .forum import bp as forum_bp

__all__ = [
    'user_bp',
    'article_bp',
    'admin_bp',
    'forum_bp'
]

__version__ = 'v1'
