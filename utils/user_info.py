import random
from models import UserModel
from .imgs import user_img_lst


def user_dict(user_id=None):
    user = UserModel.query.filter(UserModel.user_id == user_id).first()
    if user is not None:
        return obj_to_dict(user)
    else:
        return None


def obj_to_dict(user=None):
    if user is not None:
        return dict(username=user.username, avatar=user.avatar, email=user.email,
                    user_id=user.user_id, tags=user.tags)
    else:
        return dict()
