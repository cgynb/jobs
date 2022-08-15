from flask_socketio import (emit,
                            rooms,
                            join_room,
                            leave_room,
                            close_room,
                            disconnect,
                            participants,
                            Namespace)
from flask import request, copy_current_request_context
from exts import db
from models import ChatMapModel, RoomModel
from utils.user_info import user_dict


class ChatNamespace(Namespace):
    # 连接是触发
    def on_connect(self):
        # rooms =
        # emit('get_rooms', {'rooms': ...})
        print('con!!')

    def on_join_rooms(self, message):
        user_id = message.get('user_id')
        user_sid = request.sid

        user_obj = ChatMapModel.query.filter(ChatMapModel.user_id == user_id).first()
        if user_obj is None:
            u = ChatMapModel(user_id=user_id, user_sid=user_sid)
            db.session.add(u)
        else:
            user_obj.user_sid = user_sid
        db.session.commit()

        sql = """
            select room.room_id, user1_id, user2_id from room where room.user1_id = :user_id
            union all
            select room.room_id, user1_id, user2_id from room where room.user2_id = :user_id;
        """
        for room_id, _, _ in db.session.execute(sql, params={'user_id': user_id}).fetchall():
            emit('other_join', {'data': {'new_user': user_dict(user_id)}}, room=room_id)
            join_room(room_id)

        rm_ids = rooms()
        rm_ids.remove(user_sid)
        rs = []
        for r in rm_ids:
            user_sids = participants(r)
            mp = []
            for user_sid in user_sids:
                user_id = ChatMapModel.query.filter(ChatMapModel.user_sid == user_sid).first().user_id
                mp.append({'user': user_dict(user_id)})
            rs.append({'room_id': r, 'participants': mp})
        emit('get_rooms', {'rooms': rs, 'user_sid': user_sid})

    # 断开连接触发
    # def on_disconnect(self):
    #     print('Client disconnected', request.sid)

    # 自己发送信息
    # def on_my_event(self, message):
    #     print(message)
    #     print(message['data'])
    #     emit('resp',
    #          {'data': message['data']})

    # 断开连接
    # def on_disconnect_request(self):
    #     @copy_current_request_context
    #     def can_disconnect():
    #         disconnect()
    #
    #     emit('resp', {'data': 'Disconnected!'}, callback=can_disconnect)

    # 在房间中发送信息
    def on_send_room_msg(self, message):
        emit('get_room_msg', {'data': message['data']}, room=message.get('room'))

    # 关闭房间
    def on_close_room(self, message):
        emit('resp', {'data': 'the room is close'}, room=message.get('room_id'))

        room = RoomModel.query.filter(RoomModel.room_id == message.get('room_id'))
        db.session.delete(room)
        db.session.commit()

        close_room(message['room'])

    # 离开房间
    def on_leave(self, message):
        emit('resp', {'data': user_dict(message.get('user_id'))})
        leave_room(message['room'])

    # 广播
    # def on_my_broadcast_event(self, message):
    #     emit('resp', {'data': message['data']}, broadcast=True)
