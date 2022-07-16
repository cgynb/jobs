import string
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from smtplib import SMTPException
from flask import Blueprint, request, jsonify, g, current_app
from flask.views import MethodView
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import random
from exts import db, mail
from models import UserModel, CaptchaModel
from utils.token_operation import validate_token
from utils.log import Log

bp = Blueprint('user', __name__, url_prefix='/api/v1/user')


@bp.route('/login/', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        cur_user = UserModel.query.filter(UserModel.username == username).first()
    except SQLAlchemyError as e:
        Log.error(e)
    else:
        if cur_user is None:
            return jsonify({'code': 404, 'message': "there's no such user"})
        if check_password_hash(cur_user.password, password):
            g.user = cur_user
            g.login = True
            user_dict = g.user.__dict__
            user_dict.pop('_sa_instance_state')
            user_dict.pop('id')
            user_dict.pop('password')
            # print(user_dict)
            return jsonify({'code': 200, 'message': 'success', 'data': user_dict})
        else:
            return jsonify({'code': 403, 'message': 'your password is wrong'})


@bp.route('/refresh/', methods=['POST'])
def refresh():
    refresh_token = request.form.get('refresh_token')
    token, msg = validate_token(refresh_token)
    if msg is None:
        try:
            user = UserModel.query.filter(UserModel.user_id == token.get('user_id')).first()
        except SQLAlchemyError as e:
            Log.error(e)
        else:
            g.user = user
        return jsonify({'code': 200, 'message': 'success'})
    else:
        return jsonify({'code': 403, 'message': "your refresh token is wrong"})


class CaptchaAPI(MethodView):
    def get(self):  # 4-8位的验证码
        email = request.args.get('email')
        captcha_len = random.randint(4, 8)
        ret = ''.join((string.digits + string.ascii_letters)[random.randint(0, 61)] for _ in range(captcha_len))
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
            user_id = ''.join((string.digits+string.ascii_letters)[random.randint(0, 61)] for _ in range(5)) + \
                      '{0:%m%d%H%M%S%f}'.format(datetime.datetime.now())
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

    def put(self):  # 修改密码
        email = request.form.get('email')
        new_pwd = request.form.get('password')
        captcha_str = request.form.get('captcha')
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


bp.add_url_rule('/', view_func=UserAPI.as_view('user'), methods=['POST', 'PUT'])
bp.add_url_rule('/captcha/', view_func=CaptchaAPI.as_view('captcha'), methods=['GET', 'POST'])

