from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from exts import mongo
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError

bp = Blueprint('article', __name__, url_prefix='/api/v1/article')


class ArticleAPI(MethodView):
    def get(self):
        # ids为样例，gbq给的接口 (传入user_id进行分析) -> 给到文章id的列表
        ids: list = ['62d18f81b54eb0964c04918e', '62d18f81b54eb0964c049190']

        articles: list = []
        search_condition: list = [{'_id': ObjectId(i)} for i in ids]
        try:
            for c in search_condition:
                a: dict = mongo.db.article.find_one(c)
                a['_id'] = str(a['_id'])
                articles.append(a)
            return jsonify({'code': 200, 'message': 'success', 'data': articles})
        except PyMongoError:
            return jsonify({'code': 500, 'message': 'database error'})


bp.add_url_rule('/', view_func=ArticleAPI.as_view('article'))
