from flask_socketio import (emit,
                            rooms,
                            join_room,
                            leave_room,
                            close_room,
                            disconnect,
                            participants,
                            Namespace)
from flask import request, copy_current_request_context


class ChatNamespace(Namespace):
    # 连接是触发
    def on_connect(self):
        emit('my_response', {'data': 'Connected'})

    # 断开连接触发
    def on_disconnect(self):
        print('Client disconnected', request.sid)

    # 自己发送信息
    def on_my_event(self, message):
        print(message)
        print(message['data'])
        emit('my_response',
             {'data': message['data']})

    # 断开连接
    def on_disconnect_request(self):  # TODO: 删除通话
        @copy_current_request_context
        def can_disconnect():
            disconnect()

        emit('my_response', {'data': 'Disconnected!'}, callback=can_disconnect)

    # 在房间中发送信息
    def on_my_room_event(self, message):
        emit('my_response',
             {'data': message['data']}, room=message['room'])

    # 关闭房间
    def on_close_room(self, message):
        emit('my_response', {'data': 'the room called' + message['room'] + ' is closing.'}, room=message['room'])
        close_room(message['room'])

    # 离开房间
    def on_leave(self, message):
        leave_room(message['room'])
        emit('my_response', {'data': 'current in rooms: ' + str(rooms())})

    # 房间
    def on_join(self, message):
        join_room(message['room'])
        print(participants(message['room']))
        emit('my_response', {'data': 'current rooms: ' + str(rooms()) + f'participants(room: {message["room"]})' + str(participants(message['room']))},
             room=message['room'])

    # 广播
    def on_my_broadcast_event(self, message):
        emit('my_response', {'data': message['data']}, broadcast=True)
