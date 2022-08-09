from pymongo.errors import PyMongoError
from flask import jsonify, request, g
from flask.views import MethodView
import uuid
import time
import ast
import typing as t
from exts import mongo
from utils.limit import Limiter
from utils.log import Log
from utils.user_info import obj_to_dict, user_dict


class AnswerAPI(MethodView):
    def get(self):
        try:
            answer_ids: list[str] = ast.literal_eval(request.args.get('answer_ids'))
            if isinstance(answer_ids, list):
                answer_ids = answer_ids[: 5]
            else:
                return jsonify({'code': 400, 'message': f'params error ({request.args.get("answer_ids")})'})
            answers = list(mongo.db.answer.find({'answer_id': {'$in': answer_ids}}, {'_id': 0}))  # TODO type hint
            for i in range(len(answers)):
                user_id: str = answers[i].pop('user_id')
                user: t.Mapping[str, t.Union[str, list[str]]] = user_dict(user_id)
                answers[i]['user'] = user
            return jsonify({'code': 200, 'message': 'success', 'data': answers})
        except ValueError as e:
            Log.error(e)
            return jsonify({'code': 400, 'message': f'params error ({request.args.get("answer_ids")})'})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})

    @Limiter()
    @Limiter('speaker')
    def post(self):
        question_id: str = request.form.get('question_id')
        answer_content: str = request.form.get('content')
        answer_id: str = 'answer-' + str(uuid.uuid1())
        send_time: str = str(int(time.time()))
        user: t.Mapping[str, t.Union[str, list[str]]] = obj_to_dict(g.user)
        try:
            mongo.db.question.update_one({'question_id': question_id}, {'$addToSet': {'answer_ids': answer_id}})
            mongo.db.answer.insert_one({'answer_id': answer_id, 'answer_content': answer_content,
                                        'send_time': send_time, 'user_id': g.user.user_id, 'username': g.user.username})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})
        return jsonify({'code': 200, 'message': 'success',
                        'data': {'answer_content': answer_content, 'answer_id': answer_id,
                                 'send_time': send_time, 'user': user}})
