from flask import Response, request, jsonify, g
from flask.views import MethodView
import datetime
import ast
import os
import typing as t
from qcloud_cos import CosClientError, CosServiceError
from werkzeug.security import generate_password_hash
from models import CaptchaModel, UserModel
from exts import db
from utils.others import rand_str
from utils.user_info import upload_avatar, obj_to_dict
from utils.log import Log
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class UserAPI(MethodView):
    def post(self) -> Response:  # 注册用户 1. 用户名 2. 密码 3. 邮箱 4. 验证码
        username: str = request.form.get('username')
        password: str = generate_password_hash(request.form.get('password'))
        email: str = request.form.get('email')
        c_str: str = request.form.get('captcha')
        c_obj: CaptchaModel = CaptchaModel.query.filter(CaptchaModel.captcha == c_str).first()
        if c_obj:
            user_id: str = rand_str(5) + '{0:%m%d%H%M%S%f}'.format(datetime.datetime.now())
            if len(password) < 6:
                return jsonify({'code': 403, 'message': 'your password is too short'})
            try:
                cur_user: UserModel = UserModel(user_id=user_id, username=username, password=password, email=email)
                db.session.add(cur_user)
                db.session.commit()
            except IntegrityError:  # 这里不打日志，因为可以明确这是由于unique字段重复导致
                return jsonify({'code': 403, 'message': 'the email has been registered'})
            except SQLAlchemyError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
            return jsonify({'code': 200, 'message': 'success'})
        else:
            return jsonify({'code': 400, 'message': 'your captcha is wrong'})

    def put(self) -> Response:  # 修改用户信息 1. 忘记密码 2. 修改用户名 3. 头像
        email: str = request.form.get('email')
        new_pwd: str = request.form.get('password')
        captcha_str: str = request.form.get('captcha')

        new_username: str = request.form.get('username')
        try:
            if request.form.get('tags') is not None:
                new_tags: t.Optional[list[str]] = ast.literal_eval(request.form.get('tags'))
                if not isinstance(new_tags, list):
                    return jsonify({'code': 400, 'message': 'tags format error (need a list)'})
                elif len(new_tags) > 7:
                    return jsonify({'code': 400, 'message': 'up to 7 tags'})
                elif not all(len(_) <= 10 for _ in new_tags):
                    return jsonify({'code': 400, 'message': 'some of these tags is too long (limit 10 characters)'})
            else:
                new_tags = None
        except TypeError as e:  # 需要列表中都是str
            Log.error(e)
            return jsonify({'code': 400, 'message': 'tags format error (need list[str])'})
        except ValueError as e:  # 传过来的tags列表字符串有问题
            Log.error(e)
            return jsonify({'code': 400, 'message': 'tags format error (the list is not safety)'})

        new_avatar: t.Any = request.files.get('avatar')

        if captcha_str is not None and new_pwd is not None:
            if len(new_pwd) < 6:
                return jsonify({'code': 403, 'message': 'your password is too short'})
            try:
                user: UserModel = UserModel.query.filter(UserModel.email == email).first()
                c_obj: CaptchaModel = CaptchaModel.query.filter(CaptchaModel.captcha == captcha_str).first()
                if user and c_obj:
                    user.password = generate_password_hash(new_pwd)
                    db.session.commit()
                    return jsonify({'code': 200, 'message': 'success'})
                elif user is None:
                    return jsonify({'code': 400, 'message': "your email is wrong"})
                elif c_obj is None:
                    return jsonify({'code': 400, 'message': "your captcha is wrong"})
            except SQLAlchemyError as e:
                Log.error(e)
        elif new_username is not None and new_tags is not None:
            if hasattr(g, 'user') and g.user is not None:
                try:
                    check_user: UserModel = UserModel.query.filter(UserModel.username == new_username).first()
                    if check_user is None or check_user.username == g.user.username:
                        user: UserModel = UserModel.query.filter(UserModel.user_id == g.user.user_id).first()
                        user.username = new_username
                        user.tags = str(new_tags)
                        db.session.commit()
                        return jsonify({'code': 200, 'message': 'success', 'data': obj_to_dict(user)})
                    else:
                        return jsonify({'code': 403, 'message': 'this name has been used'})
                except SQLAlchemyError as e:
                    Log.error(e)
                    return jsonify({'code': 500, 'message': 'database error'})
            else:
                return jsonify({'code': 403, 'message': 'login required'})
        elif new_avatar is not None:
            if hasattr(g, 'user') and g.user is not None:
                try:
                    suffix: str = os.path.splitext(new_avatar.filename)[-1]
                    upload_avatar(g.user.user_id, new_avatar, suffix)
                    user: UserModel = UserModel.query.filter(UserModel.user_id == g.user.user_id).first()
                    user.avatar = f'https://byszqq-1310478750.cos.ap-nanjing.myqcloud.com/{g.user.user_id}{suffix}'
                    db.session.commit()
                except SQLAlchemyError as e:
                    Log.error(e)
                    return jsonify({'code': 200, 'message': 'database error'})
                except CosClientError as e:
                    Log.error(e)
                    return jsonify({'code': 500, 'message': 'cos client error'})
                except CosServiceError as e:
                    Log.error(e)
                    return jsonify({'code': 500, 'message': 'cos server error'})
                else:
                    return jsonify({'code': 200, 'message': 'success', 'data': obj_to_dict(user)})
            else:
                return jsonify({'code': 403, 'message': 'login required'})
        else:
            return jsonify({'code': 400, 'message': 'lost params'})
