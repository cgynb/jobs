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
        user.__dict__.pop('_sa_instance_state')
        user.__dict__.pop('password')
        user.__dict__.pop('id')
        if user.__dict__['avatar'] is None:
            user.__dict__['avatar'] = user_img_lst[random.randint(0, len(user_img_lst)-1)]
        return user.__dict__
    else:
        return dict()
