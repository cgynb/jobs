from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from smtplib import SMTPException
from flask import Blueprint, request, jsonify, g, current_app
from flask.views import MethodView
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import datetime
import random
import os
from exts import db, mail
from models import UserModel, CaptchaModel
from utils.token_operation import validate_token
from utils.log import Log
from utils.user_info import obj_to_dict, upload_avatar
from utils.others import rand_str

bp = Blueprint('user', __name__, url_prefix='/api/v1/user')


class LoginAPI(MethodView):
    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            cur_user = UserModel.query.filter(UserModel.username == username).first()
        except SQLAlchemyError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})
        else:
            if cur_user is None:
                return jsonify({'code': 404, 'message': "there's no such user"})
            if check_password_hash(cur_user.password, password):
                g.user = cur_user
                g.login = True
                return jsonify({'code': 200, 'message': 'success', 'data': obj_to_dict(g.user)})
            else:
                return jsonify({'code': 403, 'message': 'your password is wrong'})


class RefreshAPI(MethodView):
    def post(self):
        refresh_token = request.form.get('refresh_token')
        token, msg = validate_token(refresh_token, refresh_token=True)
        g.refresh = False
        if msg is None:
            try:
                user = UserModel.query.filter(UserModel.user_id == token.get('user_id')).first()
            except SQLAlchemyError as e:
                Log.error(e)
            else:
                g.user = user
            return jsonify({'code': 200, 'message': 'success'})
        else:
            return jsonify({'code': 403, 'message': 'please login again'})


class CaptchaAPI(MethodView):
    def get(self):  # 4-8位的验证码
        email = request.args.get('email')
        captcha_len = random.randint(4, 8)
        ret = rand_str(captcha_len)
        if email:
            try:
                c = CaptchaModel.query.filter(CaptchaModel.email == email).first()
                if c:
                    c.captcha = ret
                else:
                    c = CaptchaModel(email=email, captcha=ret)
                    db.session.add(c)
                db.session.commit()
                message = Message(
                    subject='求职',
                    recipients=[email],
                    body=f'验证码是：{ret}，请不要告诉他人',
                )
                mail.send(message)
            except SMTPException as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'smtp error'})
            except SQLAlchemyError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
            else:
                return jsonify({'code': 200, 'message': 'success'})
        else:
            return jsonify({'code': 400, 'message': 'lose params'})

    def post(self):
        email = request.form.get('email')
        c_str = request.form.get('captcha')
        try:
            c_obj = CaptchaModel.query.filter(CaptchaModel.email == email).first()
        except SQLAlchemyError as e:
            Log.error(e)
        else:
            if c_obj:
                if c_obj.captcha == c_str:
                    return jsonify({'code': 200, 'message': 'success'})
        return jsonify({'code': 200, 'message': "fail"})


class UserAPI(MethodView):
    def post(self):  # 注册用户 1. 用户名 2. 密码 3. 邮箱 4. 验证码
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))
        email = request.form.get('email')
        c_str = request.form.get('captcha')
        c_obj = CaptchaModel.query.filter(CaptchaModel.captcha == c_str).first()
        if c_obj:
            user_id = rand_str(5) + '{0:%m%d%H%M%S%f}'.format(datetime.datetime.now())
            if len(password) < 6:
                return jsonify({'code': 403, 'message': 'your password is too short'})
            try:
                cur_user = UserModel(user_id=user_id, username=username, password=password, email=email)
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

    def put(self):  # 修改用户信息
        email = request.form.get('email')
        new_pwd = request.form.get('password')
        captcha_str = request.form.get('captcha')

        new_username = request.form.get('username')
        new_tags = request.form.get('tags')

        new_avatar = request.files.get('avatar')
        if captcha_str is not None and new_pwd is not None:
            if len(new_pwd) < 6:
                return jsonify({'code': 403, 'message': 'your password is too short'})
            try:
                user = UserModel.query.filter(UserModel.email == email).first()
                c_obj = CaptchaModel.query.filter(CaptchaModel.captcha == captcha_str).first()
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
        elif new_tags is not None and new_username is not None:
            if hasattr(g, 'user') and g.user is not None:
                try:
                    user = UserModel.query.filter(UserModel.user_id == g.user.user_id).first()
                    user.tags = new_tags
                    user.username = new_username
                    user.avatar = new_avatar
                    db.session.commit()
                except SQLAlchemyError as e:
                    Log.error(e)
                    return jsonify({'code': 500, 'message': 'database error'})
                else:
                    user = UserModel.query.filter(UserModel.user_id == g.user.user_id).first()
                    return jsonify({'code': 200, 'message': 'success', 'data': obj_to_dict(user)})
            else:
                return jsonify({'code': 403, 'message': 'login required'})
        elif new_avatar is not None:
            if hasattr(g, 'user') and g.user is not None:
                try:
                    suffix = os.path.splitext(new_avatar.filename)[-1]
                    upload_avatar(g.user.user_id, new_avatar, suffix)
                    user = UserModel.query.filter(UserModel.user_id == g.user.user_id).first()
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
                    return jsonify({'code': 200, 'message': 'success', 'data': user.avatar})
            else:
                return jsonify({'code': 403, 'message': 'login required'})
        else:
            return jsonify({'code': 400, 'message': 'lost params'})


bp.add_url_rule('/', view_func=UserAPI.as_view('user'), methods=['POST', 'PUT'])
bp.add_url_rule('/captcha/', view_func=CaptchaAPI.as_view('captcha'), methods=['GET', 'POST'])
bp.add_url_rule('/login/', view_func=LoginAPI.as_view('login'), methods=['POST'])
bp.add_url_rule('/refresh/', view_func=RefreshAPI.as_view('refresh'), methods=['POST'])
