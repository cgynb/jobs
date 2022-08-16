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
from models import ChatMapModel, RoomModel, MessageModel
from utils.user_info import user_dict


def sid_to_id(sid):
    return ChatMapModel.query.filter(ChatMapModel.user_sid == sid).first().user_id


def online_user_ids():
    online_users = set()
    for room in rooms():
        if room == request.sid:
            continue
        online_users.update(sid_to_id(sid) for sid in participants(room))
    return list(online_users)


class ChatNamespace(Namespace):

    def on_join_rooms(self, data):
        user_id = data.get('user_id')
        if user_id is not None:
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
            rms = []
            for room_id, user1_id, user2_id in db.session.execute(sql, params={'user_id': user_id}).fetchall():
                join_room(room_id)
                rms.append({'room_id': room_id, 'users': [user_dict(user1_id), user_dict(user2_id)]})
                emit('user_change', {'new_user': user_dict(user_id), 'room_id': room_id}, room=room_id)

            emit('get_rooms_info', {'rooms': rms, 'user_sid': user_sid, 'online_users': online_user_ids()})
        else:
            emit('sys_msg', {'msg': 'need user_id'})

    # 在房间中发送信息
    def on_send_room_msg(self, data):
        msg = data.get('message')
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        users = participants(room_id)
        read = True if len(users) == 2 else False
        room = RoomModel.query.filter(RoomModel.room_id == room_id).first()
        reader_id = room.user1_id if user_id == room.user1_id else room.user2_id
        m = MessageModel(room_id=room_id, sender_id=user_id, reader_id=reader_id, read=read)
        db.session.add(m)
        db.session.commit()
        emit('get_room_msg', {'message': msg, 'user': user_dict(user_id)}, room=room_id)

    # 离开房间
    def on_disconnect(self):
        user = user_dict(ChatMapModel.query.filter(ChatMapModel.user_sid == request.sid).first().user_id)
        for room_id in rooms():
            if room_id == request.sid:
                continue
            emit('user_change', {'leave_user': user, 'room_id': room_id}, room=room_id)

    # 广播
    # def on_my_broadcast_event(self, message):
    #     emit('resp', {'data': message['data']}, broadcast=True)

    # 断开连接
    # def on_disconnect_request(self):
    #     @copy_current_request_context
    #     def can_disconnect():
    #         disconnect()
    #
    #     emit('resp', {'data': 'Disconnected!'}, callback=can_disconnect)
