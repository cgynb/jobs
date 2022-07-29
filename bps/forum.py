from flask import Blueprint, jsonify
from flask.views import MethodView
from exts import mongo

bp = Blueprint('article', __name__, url_prefix='/api/v1/forum')


class QuestionAPI(MethodView):
    def get(self):
        ...

    def post(self):
        mongo.db.question.insert_one()
        return jsonify({'code': 200, 'message': 'success'})


class AnswerAPI(MethodView):
    def get(self):
        ...

    def post(self):
        ...

    def delete(self):
        ...


bp.add_url_rule('/question/', view_func=QuestionAPI.as_view('question'))
bp.add_url_rule('/answer/', view_func=AnswerAPI.as_view('answer'))
