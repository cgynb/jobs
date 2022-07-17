from flask import Blueprint, request, jsonify, g, current_app
from flask.views import MethodView
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from exts import mongo, db
from models import LikeModel, CollectModel
from utils.log import Log
from utils.role_limit import login_required

bp = Blueprint('article', __name__, url_prefix='/api/v1/article')


class ArticleAPI(MethodView):
    # @login_required
    def get(self):
        # TODO: ids为样例，gbq给的接口 (传入user_id进行分析) -> 给到文章id的列表
        ids: list = ['62d3b144551ed4ee99d0e08a', '62d3b144551ed4ee99d0e08b']

        articles: list = []
        search_condition: list = [{'_id': ObjectId(i)} for i in ids]
        try:
            for c in search_condition:
                a: dict = mongo.db.article.find_one(c)
                a['_id'] = str(a['_id'])
                articles.append(a)
            return jsonify({'code': 200, 'message': 'success', 'data': articles})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})

    def post(self):
        article_id = request.form.get('article_id')
        user_id = g.user.user_id
        commend = request.form.get('commend')
        print(article_id, user_id, commend)

        return jsonify({'code': 200, 'message': 'success'})


# like and collect
class LCAPI(MethodView):
    def get(self):
        article_id = request.args.get('article_id')
        try:
            if ObjectId.is_valid(article_id):
                article = mongo.db.article.find_one({'_id': ObjectId(article_id)})
                if article is None:
                    return jsonify({'code': 404, 'message': "there's no such article"})
                else:
                    if hasattr(g, 'user'):
                        user_id = g.user.user_id
                        like_obj = LikeModel.query.filter(LikeModel.user_id == user_id).first()
                        collect_obj = CollectModel.query.filter(CollectModel.user_id == user_id).first()
                        return jsonify({'code': 200, 'message': 'success',
                                        'data': {'article': {'like': article['like'], 'collect': article['collect']},
                                                 'user': {'like': bool(like_obj), 'collect': bool(collect_obj)}}})
                    else:
                        return jsonify({'code': 200, 'message': 'success',
                                        'data': {'article': {'like': article['like'], 'collect': article['collect']},
                                                 'user': {'like': False, 'collect': False}}})
            else:
                return jsonify({'code': 400, 'message': 'article_id invalid'})
        except SQLAlchemyError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})

    @login_required
    def put(self):
        like = str(request.form.get('like'))  # 0: 不改动 1: 点赞 -1: 取消点赞
        collect = str(request.form.get('collect'))  # 0: 不改动 1: 收藏 -1 : 取消收藏
        article_id = request.form.get('article_id')
        user_id = g.user.user_id
        if ObjectId.is_valid(article_id):
            if mongo.db.article.find_one({'_id': ObjectId(article_id)}) is None:
                return jsonify({'code': 404, 'message': "there's no such article"})
        else:
            return jsonify({'code': 400, 'message': 'article_id invalid'})
        try:
            if like != '0' and collect != '0':
                Log.warning("like/collect params error")
                return jsonify({'code': 400, 'message': 'params error'})
            elif like != '0':
                like_obj = LikeModel.query. \
                    filter(and_(LikeModel.user_id == user_id, LikeModel.article_id == article_id)).first()
                if like_obj is not None:
                    if like == '1':
                        return jsonify({'code': 400, 'message': "You've already liked this article"})
                    elif like == '-1':
                        db.session.delete(like_obj)
                        db.session.commit()
                        mongo.db.article.update_one({'_id': ObjectId(article_id)}, {'$inc': {'like': -1}})
                        return jsonify({'code': 200, 'message': 'success'})
                elif like_obj is None:
                    if like == '1':
                        like_obj = LikeModel(article_id=article_id, user_id=user_id)
                        db.session.add(like_obj)
                        db.session.commit()
                        mongo.db.article.update_one({'_id': ObjectId(article_id)}, {'$inc': {'like': 1}})
                        return jsonify({'code': 200, 'message': 'success'})
                    elif like == '-1':
                        return jsonify({'code': 400, 'message': "You've canceled the like"})
            elif collect != '0':
                collect_obj = CollectModel.query. \
                    filter(and_(CollectModel.user_id == user_id, CollectModel.article_id == article_id)).first()
                if collect_obj is not None:
                    if collect == '1':
                        return jsonify({'code': 400, 'message': "You've already collected this article"})
                    elif collect == '-1':
                        db.session.delete(collect_obj)
                        db.session.commit()
                        mongo.db.article.update_one({'_id': ObjectId(article_id)}, {'$inc': {'collect': -1}})
                        return jsonify({'code': 200, 'message': 'success'})
                elif collect_obj is None:
                    if collect == '1':
                        collect_obj = CollectModel(article_id=article_id, user_id=user_id)
                        db.session.add(collect_obj)
                        db.session.commit()
                        mongo.db.article.update_one({'_id': ObjectId(article_id)}, {'$inc': {'collect': 1}})
                        return jsonify({'code': 200, 'message': 'success'})
                    elif collect == '-1':
                        return jsonify({'code': 400, 'message': "You've canceled the collection"})
            else:
                Log.warning("like/collect params error")
                return jsonify({'code': 400, 'message': 'params error'})
        except SQLAlchemyError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})


bp.add_url_rule('/', view_func=ArticleAPI.as_view('article'), methods=['GET', 'POST'])
bp.add_url_rule('/lc/', view_func=LCAPI.as_view('like-collect'), methods=['GET', 'PUT'])
