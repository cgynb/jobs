import typing as t
from flask import request, jsonify, Response
from flask.views import MethodView
import pymongo
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from exts import mongo
from utils.log import Log
from ai_package.recommend import recommend_ids


class RecommendAPI(MethodView):
    def get(self) -> Response:
        """
        param group 1:
            获取热门文章
            lc[True]
            ai[False]
            article_id[useless]
            type[optional]
            :return: 热门文章列表
        parma group 2:
            获取ai分析文章
            lc[True]
            ai[False]
            article_id[must]
            type[useless]
            :return: ai推荐文章列表
        """
        lc: bool = True if request.args.get('lc', default=False) == 'true' else False

        ai: bool = True if request.args.get('ai', default=False) == 'true' else False
        cur_article_id = request.args.get('article_id')
        condition: t.Mapping[str, str] = \
            {'type': request.args.get('type')} if request.args.get('type') else {}
        if lc is True and ai is False:
            try:
                articles: pymongo.cursor.Cursor = mongo.db.article.find(condition, {'content': 0, 'comment': 0}). \
                    sort([('like', pymongo.DESCENDING), ('collect', pymongo.DESCENDING)]).limit(5)
                article_lst: list[dict] = list()  # TODO: type hint
                for article in articles:
                    article['_id'] = str(article['_id'])
                    article_lst.append(article)
                return jsonify({'code': 200, 'message': 'success', 'data': article_lst})
            except PyMongoError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
        elif lc is False and ai is True:
            if cur_article_id is not None:
                if ObjectId.is_valid(cur_article_id):
                    article_id_lst = recommend_ids(cur_article_id)
                    articles = mongo.db.article.find({'_id': {'$in': article_id_lst}}, {'content': 0, 'comment': 0})
                    article_lst: list[dict] = list()  # TODO: type hint
                    for article in articles:
                        article['_id'] = str(article['_id'])
                        article_lst.append(article)
                    return jsonify({'code': 200, 'message': 'success', 'data': article_lst})
                else:
                    return jsonify({'code': 400, 'message': 'article_id invalid'})
            else:
                return jsonify({'code': 400, 'message': 'lose params (current article id)'})
        elif lc is False and ai is False:
            return jsonify({'code': 400, 'message': 'params error (both false)'})
        elif lc is True and ai is True:
            return jsonify({'code': 400, 'message': 'params error (both true)'})

