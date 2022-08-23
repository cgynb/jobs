from flask_socketio import (emit,
                            rooms,
                            join_room,
                            leave_room,
                            close_room,
                            disconnect,
                            participants,
                            Namespace)
from flask import request, copy_current_request_context
from sqlalchemy.exc import SQLAlchemyError
from exts import db
from models import ChatMapModel, RoomModel, MessageModel
from utils.log import Log
from utils.user_info import user_dict
from utils.args_check import Check


def sid_to_id(sid):
    user_map = ChatMapModel.query.filter(ChatMapModel.user_sid == sid).first()
    if user_map is not None:
        return user_map.user_id


def id_to_sid(user_id):
    user_map = ChatMapModel.query.filter(ChatMapModel.user_id == user_id).first()
    if user_map is not None:
        return user_map.user_sid


def update_map(user_id, user_sid):
    try:
        user_obj = ChatMapModel.query.filter(ChatMapModel.user_id == user_id).first()
        if user_obj is None:
            u = ChatMapModel(user_id=user_id, user_sid=user_sid)
            db.session.add(u)
        else:
            user_obj.user_sid = user_sid
        db.session.commit()
    except SQLAlchemyError as e:
        Log.error(e)
        db.session.rollback()
        emit('sys_msg', {'code': 500, 'message': 'database error'})


class ChatNamespace(Namespace):

    def on_update(self, data):
        user_id = data.get('user_id')
        if Check(must=('user_id', ), args_dict=data).check():
            update_map(user_id, request.sid)
        else:
            emit('sys_msg', {'code': 400, 'message': 'params error'})

    def on_join_room(self, data):
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        if Check(must=('room_id', 'user_id'), args_dict=data).check():
            join_room(room_id)
            emit('room_info', {'code': 200, 'message': 'success',
                               'data': {'online_status': True if len(participants(room_id)) == 2 else False}},
                 callback=lambda: update_map(user_id, request.sid))
            emit('user_change', {'code': 200, 'message': 'success',
                                 'data': {'change': 'join',
                                          'user': user_dict(user_id),
                                          'room_id': room_id}
                                 }, room=room_id)
        else:
            emit('sys_msg', {'code': 400, 'message': 'params error'})

    def on_leave_room(self, data):
        room_id = data.get('room_id')
        if Check(must=('room_id', ), args_dict=data).check():
            leave_room(room_id)
            emit('sys_msg', {'code': 200, 'message': 'success'})
        else:
            emit('sys_msg', {'code': 400, 'message': 'params error'})

    # 在房间中发送信息
    def on_send_room_msg(self, data):
        msg = data.get('message')
        room_id = data.get('room_id')
        sender_id = data.get('sender_id')
        reader_id = data.get('reader_id')
        # 判断房间人数，确定这条消息是否已读
        read = True if len(participants(room_id)) == 2 else False
        if Check(must=('message', 'room_id', 'reader_id', 'sender_id'), args_dict=data).check():
            try:
                # 存储消息
                m = MessageModel(room_id=room_id, sender_id=sender_id, reader_id=reader_id, read=read)
                db.session.add(m)
                db.session.commit()
            except SQLAlchemyError as e:
                Log.error(e)
                db.session.rollback()
                emit('sys_msg', {'code': 500, 'message': 'database error'})
            else:
                if read is False:  # 如果那个人不在房间，则发送给那个人
                    emit('get_msg', {'code': 200, 'message': 'success',
                                     'data': {'message': msg,
                                              'room_id': room_id,
                                              'sender': user_dict(sender_id)}},
                         to=id_to_sid(reader_id),
                         callback=lambda: update_map(sender_id, request.sid))
                else:  # 如果那个人在房间，则发送到房间里
                    emit('get_room_msg', {'code': 200, 'message': 'success',
                                          'data': {'message': msg,
                                                   'room_id': room_id,
                                                   'sender': user_dict(sender_id)}
                                          },
                         room=room_id,
                         callback=lambda: update_map(sender_id, request.sid))
        else:
            emit('sys_msg', {'code': 400, 'message': 'params error'})

    # 离开房间
    def on_disconnect(self):
        try:
            user_map = ChatMapModel.query.filter(ChatMapModel.user_sid == request.sid).first()
        except SQLAlchemyError as e:
            Log.error(e)
            user_map = None
        if user_map is not None:
            user = user_dict(user_map.user_id)
        else:
            user = None
            emit('sys_msg', {'code': 406, 'message': 'update map'})

        for room_id in rooms():
            if room_id == request.sid:
                continue
            emit('user_change', {'code': 200, 'message': 'success',
                                 'data': {'change': 'leave',
                                          'user': user,
                                          'room_id': room_id}
                                 }, room=room_id)

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
