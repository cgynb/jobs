import string
import sqlalchemy
from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import random
from exts import db, mail
from models import UserModel, CaptchaModel
from utils.token_operation import validate_token

bp = Blueprint('user', __name__, url_prefix='/api/v1/user')


@bp.route('/login/', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    cur_user = UserModel.query.filter(UserModel.username == username).first()
    if cur_user is None:
        return jsonify({'code': 404, 'message': "there's no such user"})
    if check_password_hash(cur_user.password, password):
        g.user = cur_user
        g.login = True
        return jsonify({'code': 200, 'message': 'success'})
    else:
        return jsonify({'code': 403, 'message': 'your password is wrong'})


@bp.route('/refresh/', methods=['POST'])
def refresh():
    refresh_token = request.form.get('refresh_token')
    token, msg = validate_token(refresh_token)
    if msg is None:
        try:
            user = UserModel.query.filter(UserModel.user_id == token.get('user_id')).first()
            g.user = user
        except Exception as e:
            print(e)
        return jsonify({'code': 200, 'message': 'success'})
    else:
        return jsonify({'code': 403, 'message': "your refresh token is wrong"})


class CaptchaAPI(MethodView):
    def get(self):
        email = request.args.get('email')
        ret = ''.join((string.digits + string.ascii_letters)[random.randint(0, 61)] for _ in range(6))
        if email:
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
            return jsonify({'code': 200, 'message': 'success'})
        else:
            return jsonify({'code': 400, 'message': 'lose params'})

    def post(self):
        email = request.form.get('email')
        c_str = request.form.get('captcha')
        c_obj = CaptchaModel.query.filter(CaptchaModel.email == email).first()
        if c_obj:
            if c_obj.captcha == c_str:
                return jsonify({'code': 200, 'message': 'success'})
        return jsonify({'code': 400, 'message': "fail"})


    def put(self):
        pass

    def delete(self):
        pass


class UserAPI(MethodView):
    def get(self):
        print('get')

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
            except sqlalchemy.exc.IntegrityError:
                return jsonify({'code': 403, 'message': 'the email has been registered'})
            return jsonify({'code': 200, 'message': 'success'})
        else:
            return jsonify({'code': 400, 'message': 'your captcha is wrong'})

    def put(self):
        print(request.form.to_dict())

    def delete(self):
        print('delete')


bp.add_url_rule('/', view_func=UserAPI.as_view('user'))
bp.add_url_rule('/captcha/', view_func=CaptchaAPI.as_view('captcha'))

