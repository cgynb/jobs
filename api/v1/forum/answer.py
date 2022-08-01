from pymongo.errors import PyMongoError
from flask import Blueprint, jsonify, request, g
from flask.views import MethodView
import uuid
import time
import typing as t
from exts import mongo
from utils.role_limit import login_required
from utils.log import Log
from utils.user_info import obj_to_dict, user_dict


class AnswerAPI(MethodView):
    def get(self):
        answer_id = request.args.get('answer_id')
        answer: dict = mongo.db.answer.find_one({'answer_id': answer_id}, {'_id': 0})  # TODO: type hint
        if answer is not None:
            try:
                user_id = answer.pop('user_id')
                user = user_dict(user_id)
                answer['user'] = user
                return jsonify({'code': 200, 'message': 'success', 'data': answer})
            except PyMongoError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
        else:
            return jsonify({'code': 400, 'message': f"there's no such answer (answer_id: {answer_id})"})

    @login_required
    def post(self):
        question_id = request.form.get('question_id')
        answer_content = request.form.get('content')
        answer_id = 'answer-' + str(uuid.uuid1())
        send_time = str(int(time.time()))
        user = obj_to_dict(g.user)
        mongo.db.question.update_one({'question_id': question_id}, {'$addToSet': {'answer_ids': answer_id}})
        mongo.db.answer.insert_one({'answer_id': answer_id, 'answer_content': answer_content,
                                    'send_time': send_time, 'user_id': g.user.user_id})
        return jsonify({'code': 200, 'message': 'success',
                        'data': {'answer_content': answer_content, 'answer_id': answer_id,
                                 'send_time': send_time, 'user': user}})

    def delete(self):
        ...
