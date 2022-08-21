from flask import Response, request, jsonify, g
from flask.views import MethodView
from models import UserModel
from werkzeug.security import check_password_hash
from utils.log import Log
from utils.args_check import Check
from utils.user_info import obj_to_dict
from sqlalchemy.exc import SQLAlchemyError


class LoginAPI(MethodView):
    def post(self) -> Response:
        username: str = request.form.get('username')
        password: str = request.form.get('password')
        if Check(must=('username', 'password'), args_dict=request.form).check():
            try:
                cur_user: UserModel = UserModel.query.filter(UserModel.username == username).first()
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
        else:
            return jsonify({'code': 400, 'message': 'params error'})
