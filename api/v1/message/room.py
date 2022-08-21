from flask.views import MethodView
from flask import g, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from exts import db
from models import RoomModel
from utils.limit import Limiter
from utils.others import gen_room_id
from utils.args_check import Check


class RoomAPI(MethodView):
    @Limiter('user')
    def get(self):
        sql = """
                select room.room_id,
                       ifnull((select message.info
                        from message
                        where message.room_id = room.room_id
                        order by id DESC
                        limit 1), "send some message to your friend") as last_msg,
                       (select count(*)
                        from message
                        where message.read = false
                          and message.reader_id = :user_id
                          and message.room_id = room.room_id) as to_read
                from room
                where room.user1_id = :user_id
                
                union all
                
                select room.room_id,
                       ifnull((select message.info
                        from message
                        where message.room_id = room.room_id
                        order by id DESC
                        limit 1), "send some message to your friend") as last_msg,
                       (select count(*)
                        from message
                        where message.read = false
                          and message.reader_id = :user_id
                          and message.room_id = room.room_id) as to_read
                from room
                where room.user2_id = :user_id;
        """
        rms = list()
        for room_id, last_msg, to_read in db.session.execute(sql, params={'user_id': g.user.user_id}).fetchall():
            rms.append({'room_id': room_id, 'last_msg': last_msg, 'to_read': to_read})
        return jsonify({'code': 200, 'message': 'success', 'data': rms})

    @Limiter('user')
    def post(self):
        if Check(must=('user_id', ), args_dict=request.form).check():
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
        else:
            return jsonify({'code': 400, 'message': 'params error'})
