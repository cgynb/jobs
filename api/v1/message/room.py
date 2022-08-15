from flask.views import MethodView
from flask import g, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from exts import db
from models import RoomModel
from utils.limit import Limiter
from utils.others import gen_room_id


class RoomAPI(MethodView):
    @Limiter('user')
    def post(self):
        user_id = request.form.get('user_id')
        room_id = gen_room_id(g.user.user_id, user_id)
        try:
            r = RoomModel(room_id=room_id, user1_id=g.user.user_id, user2_id=user_id)
            db.session.add(r)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({'code': 403, 'message': 'the room has been built'})
        return jsonify({'code': 200, 'message': 'success'})
