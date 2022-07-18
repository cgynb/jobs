from models import UserModel


def user_dict(user_id=None):
    user = UserModel.query.filter(UserModel.user_id == user_id).first()
    user.__dict__.pop('_sa_instance_state')
    user.__dict__.pop('password')
    user.__dict__.pop('id')
    return user.__dict__
