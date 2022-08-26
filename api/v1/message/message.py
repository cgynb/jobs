from flask import jsonify, request, g, Response
from flask.views import MethodView
from exts import db
from models import MessageModel
from utils.args_check import Check
from utils.limit import Limiter
from utils.user_info import user_dict


class MessageAPI(MethodView):
    @Limiter('user')
    def get(self) -> Response:
        if Check(must=('room_id', ), args_dict=request.args).check():
            msgs: list = MessageModel.query.filter(MessageModel.room_id == request.args.get('room_id')).all()
            msg_lst: list = []
            for msg in msgs:
                if g.user.user_id == msg.reader_id:
                    msg.read = True
                    db.session.commit()
                msg_lst.append({'sender_id': msg.sender_id, 'reader_id': msg.reader_id,
                                'sender': user_dict(msg.sender_id),
                                'read': msg.read, 'message': msg.info, 'send_time': msg.send_time})
            return jsonify({'code': 200, 'message': 'success',
                            'data': {'messages': msg_lst}})
        else:
            return jsonify({'code': 400, 'message': 'params error'})
