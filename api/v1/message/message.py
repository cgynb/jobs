from flask import jsonify, request, g
from flask.views import MethodView
from exts import db
from models import MessageModel
from utils.args_check import Check


class MessageAPI(MethodView):
    def get(self):
        if Check(must=('room_id', ), args_dict=request.args).check():
            msgs = MessageModel.query.filter(MessageModel.room_id == request.args.get('room_id')).all()
            msg_lst = []
            for msg in msgs:
                if g.user.user_id == msg.reader_id:
                    msg.read = True
                    db.session.commit()
                msg_lst.append({'sender_id': msg.sender_id, 'reader_id': msg.reader_id,
                                'read': msg.read, 'message': msg.info})
            return jsonify({'code': 200, 'message': 'success', 'data': {'messages': msg_lst}})
        else:
            return jsonify({'code': 400, 'message': 'params error'})
