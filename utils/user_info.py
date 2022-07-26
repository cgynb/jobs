from flask import current_app
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from models import UserModel


def user_obj(user_id=None):
    user = UserModel.query.filter(UserModel.user_id == user_id).first()
    if user is not None:
        return user
    else:
        return None


def user_dict(user_id=None):
    user = UserModel.query.filter(UserModel.user_id == user_id).first()
    if user is not None:
        return obj_to_dict(user)
    else:
        return None


def obj_to_dict(user=None):
    if user is not None:
        return dict(username=user.username, avatar=user.avatar, email=user.email,
                    user_id=user.user_id, tags=tag_str_to_lst(user.tags))
    else:
        return dict()


def tag_str_to_lst(tag_str):
    if tag_str is None:
        return list()
    return tag_str.split('|')[:-1]


def tag_lst_to_str(tag_lst):
    if not tag_lst:
        return None
    else:
        return '|'.join(tag_lst) + '|'


def upload_avatar(user_id, photo_obj, suffix):
    config = CosConfig(Region=current_app.config.get('COS_REGION'),
                       SecretId=current_app.config.get('COS_SECRET_ID'),
                       SecretKey=current_app.config.get('COS_SECRET_KEY'))
    client = CosS3Client(config)
    client.put_object(
        Bucket=current_app.config.get('COS_BUCKET'),
        Body=photo_obj,
        Key=f'{user_id}{suffix}',
        StorageClass='STANDARD',
    )
