from flask import Response, request, g, jsonify
from flask.views import MethodView
from utils.log import Log
from utils.token_operation import validate_token
from models import UserModel
from sqlalchemy.exc import SQLAlchemyError


class RefreshAPI(MethodView):
    def post(self) -> Response:
        refresh_token: str = request.form.get('refresh_token')
        token, msg = validate_token(refresh_token, refresh_token=True)
        g.refresh = False
        if msg is None:
            try:
                user: UserModel = UserModel.query.filter(UserModel.user_id == token.get('user_id')).first()
            except SQLAlchemyError as e:
                Log.error(e)
            else:
                g.user = user
            return jsonify({'code': 200, 'message': 'success'})
        else:
            return jsonify({'code': 403, 'message': 'please login again'})
