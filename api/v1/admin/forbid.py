from flask import request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from models import UserModel
from exts import db
from utils.args_check import Check
from utils.log import Log
from utils.limit import Limiter


class ForbidAPI(MethodView):
    @Limiter('admin')
    def put(self):
        user_id = request.form.get('user_id')
        forbid = request.form.get('forbid')
        if Check(must=('user_id', 'forbid'), args_dict=request.form).check():
            try:
                user = UserModel.query.filter(UserModel.user_id == user_id).first()
                user.forbid = forbid
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
            return jsonify({'code': 200, 'message': 'success'})
        else:
            return jsonify({'code': 400, 'message': 'params error'})
