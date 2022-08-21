from flask import Response, request, jsonify
from flask.views import MethodView
import random
from models import CaptchaModel
from exts import db, mail
from flask_mail import Message
from utils.others import rand_str
from utils.log import Log
from utils.args_check import Check
from sqlalchemy.exc import SQLAlchemyError
from smtplib import SMTPException


class CaptchaAPI(MethodView):
    def get(self) -> Response:  # 4-8位的验证码
        email: str = request.args.get('email')
        captcha_len: int = random.randint(4, 8)
        ret: str = rand_str(captcha_len)
        if Check(must=('email', ), args_dict=request.args).check():
            try:
                c: CaptchaModel = CaptchaModel.query.filter(CaptchaModel.email == email).first()
                if c:
                    c.captcha = ret
                else:
                    c: CaptchaModel = CaptchaModel(email=email, captcha=ret)
                    db.session.add(c)
                db.session.commit()
                message: Message = Message(
                    subject='毕业剩转圈圈',
                    recipients=[email],
                    body=f'验证码是：{ret}，请不要告诉他人',
                )
                mail.send(message)
                return jsonify({'code': 200, 'message': 'success'})
            except SMTPException as e:
                Log.error(e)
                db.session.rollback()
                return jsonify({'code': 500, 'message': 'smtp error'})
            except SQLAlchemyError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
        else:
            return jsonify({'code': 400, 'message': 'params error'})

    def post(self) -> Response:
        email: str = request.form.get('email')
        c_str: str = request.form.get('captcha')
        try:
            c_obj: CaptchaModel = CaptchaModel.query.filter(CaptchaModel.email == email).first()
        except SQLAlchemyError as e:
            Log.error(e)
        else:
            if c_obj is not None:
                if c_obj.captcha == c_str:
                    return jsonify({'code': 200, 'message': 'success'})
        return jsonify({'code': 200, 'message': "fail"})
