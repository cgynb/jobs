from flask import Blueprint, jsonify, request, g
from flask.views import MethodView
import uuid
import time
from exts import mongo
from utils.role_limit import login_required

bp = Blueprint('forum', __name__, url_prefix='/api/v1/forum')


class QuestionAPI(MethodView):
    def get(self):
        ...

    @login_required
    def post(self):
        title = request.form.get('title')
        content = request.form.get('content')
        send_time = str(int(time.time()))
        question_id = 'question-' + str(uuid.uuid1())
        mongo.db.question.insert_one({'question_id': question_id, 'question_title': title,
                                      'question_content': content, 'user_id': g.user.user_id,
                                      'send_time': send_time, 'answer_ids': []})
        return jsonify({'code': 200, 'message': 'success',
                        'data': {'question_id': question_id, 'question_title': title, 'user_id': g.user.user_id,
                                 'question_content': content, 'send_time': send_time, 'answer_ids': []}})


class AnswerAPI(MethodView):
    def get(self):
        ...

    def post(self):
        ...

    def delete(self):
        ...


bp.add_url_rule('/question/', view_func=QuestionAPI.as_view('question'))
bp.add_url_rule('/answer/', view_func=AnswerAPI.as_view('answer'))
