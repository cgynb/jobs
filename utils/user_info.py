import typing as t
import ast
from flask import current_app
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from models import UserModel


def user_obj(user_id: str = None) -> t.Optional[UserModel]:
    user = UserModel.query.filter(UserModel.user_id == user_id).first()
    if user is not None:
        return user
    else:
        return None


def user_dict(user_id: str = None) -> t.Optional[dict]:
    user = UserModel.query.filter(UserModel.user_id == user_id).first()
    if user is not None:
        return obj_to_dict(user)
    else:
        return {}


def obj_to_dict(user: UserModel = None) -> dict:
    if user is not None:
        return dict(username=user.username, avatar=user.avatar, email=user.email, role=user.role,
                    forbid=user.forbid, user_id=user.user_id, tags=ast.literal_eval(user.tags))
    else:
        return dict()


def upload_photo(photo_obj, photo_name: str, suffix: str) -> None:
    config = CosConfig(Region=current_app.config.get('COS_REGION'),
                       SecretId=current_app.config.get('COS_SECRET_ID'),
                       SecretKey=current_app.config.get('COS_SECRET_KEY'))
    client = CosS3Client(config)
    client.put_object(
        Bucket=current_app.config.get('COS_BUCKET'),
        Body=photo_obj,
        Key=f'{photo_name}{suffix}',
        StorageClass='STANDARD',
    )
