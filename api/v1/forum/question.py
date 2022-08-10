from pymongo.errors import PyMongoError
from flask import jsonify, request, g
from flask.views import MethodView
import uuid
import time
import typing as t
from exts import mongo
from utils.limit import Limiter
from utils.log import Log
from utils.user_info import user_dict


class QuestionAPI(MethodView):
    def get(self):
        """
        param group 1:
            question_id[must]
            page[useless]
            username[useless]
            title[useless]
            :return: 提问内容
        param group 2:
            question_id[mustn't]
            page[optional]
            username[optional]
            title[optional]
            :return: 提问列表
        """
        question_id: t.Optional[str] = request.args.get('question_id')

        page: t.Optional[str] = request.args.get('page')
        username: t.Optional[str] = request.args.get('username')
        title: t.Optional[str] = request.args.get('title')
        try:
            if question_id is not None:
                question = mongo.db.question.find_one({'question_id': question_id}, {'_id': 0})
                question |= user_dict(question.get('user_id'))
                return jsonify({'code': 200, 'message': 'success', 'data': question})
            else:
                each_page = 10
                condition = dict()
                if username is not None:
                    condition['username'] = {'$regex': f'.*{username}.*'}
                elif title is not None:
                    condition['question_title'] = {'$regex': f'.*{title}.*'}
                total_question = mongo.db.question.count_documents(condition)
                total_page = total_question // each_page + 1 if total_question % each_page else total_question // each_page
                questions = mongo.db.question.find(condition, {'_id': 0, 'answer_ids': 0}).sort(
                    [('send_time', -1)]).limit(each_page).skip((int(page) - 1) * each_page)

                question_lst = [question for question in questions]
                for i in range(len(question_lst)):
                    question_lst[i] |= user_dict(question_lst[i].get('user_id'))
                return jsonify({'code': 200, 'message': 'success',
                                'data': {'current_page': page, 'total_question': total_question,
                                         'total_page': total_page, 'questions': question_lst}})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})

    @Limiter('speaker')
    def post(self):
        try:
            question_title = request.form.get('title')
            question_content = request.form.get('content')
            send_time = str(int(time.time()))
            question_id = 'question-' + str(uuid.uuid1())
            mongo.db.question.insert_one({'question_id': question_id, 'question_title': question_title,
                                          'question_content': question_content,
                                          'user_id': g.user.user_id, 'username': g.user.username,
                                          'send_time': send_time, 'answer_ids': []})
            return jsonify({'code': 200, 'message': 'success',
                            'data': {'question_id': question_id, 'question_title': question_title,
                                     'user_id': g.user.user_id, 'username': g.user.username,
                                     'question_content': question_content,
                                     'send_time': send_time, 'answer_ids': []}})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})

    @Limiter('admin')
    def delete(self):  # TODO: 删除回答
        ...
