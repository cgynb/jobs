from flask import request, jsonify
from flask.views import MethodView
from models import UserModel
from exts import db
from utils.limit import Limiter


class ForbidAPI(MethodView):
    @Limiter('admin')
    def put(self):
        user_id = request.form.get('user_id')
        forbid = request.form.get('forbid')
        user = UserModel.query.filter(UserModel.user_id == user_id).first()
        user.forbid = forbid
        db.session.commit()
        return jsonify({'code': 200, 'message': 'success'})
