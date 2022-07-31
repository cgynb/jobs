from pymongo.errors import PyMongoError
from flask import Blueprint, jsonify, request, g
from flask.views import MethodView
import uuid
import time
import typing as t
from exts import mongo
from utils.role_limit import login_required
from utils.log import Log

bp = Blueprint('question', __name__, url_prefix='/question')


class QuestionAPI(MethodView):
    def get(self):
        """
        param group 1:
            question_id[must]
            page[useless]
            :return: 提问内容
        param group 2:
            question_id[mustn't]
            page[optional]
            :return: 提问列表
        """
        question_id: t.Optional[str] = request.args.get('question_id')
        page: t.Optional[str] = request.args.get('page')
        try:
            if question_id is not None:
                question = mongo.db.question.find_one({'question_id': question_id}, {'_id': 0})
                return jsonify({'code': 200, 'message': 'success', 'data': question})
            else:
                total_page = 0
                total_question = 0
                questions = mongo.db.question.find({}, {'_id': 0, 'answer_ids': 0}).limit(10)
                question_lst = [question for question in questions]
                return jsonify({'code': 200, 'message': 'success',
                                'data': {'current_page': page, 'total_question': total_question,
                                         'total_page': total_page, 'questions': question_lst}})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})

    @login_required
    def post(self):
        try:
            question_title = request.form.get('title')
            question_content = request.form.get('content')
            send_time = str(int(time.time()))
            question_id = 'question-' + str(uuid.uuid1())
            mongo.db.question.insert_one({'question_id': question_id, 'question_title': question_title,
                                          'question_content': question_content, 'user_id': g.user.user_id,
                                          'send_time': send_time, 'answer_ids': []})
            return jsonify({'code': 200, 'message': 'success',
                            'data': {'question_id': question_id, 'question_title': question_title,
                                     'user_id': g.user.user_id, 'question_content': question_content,
                                     'send_time': send_time, 'answer_ids': []}})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})