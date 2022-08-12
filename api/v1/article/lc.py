from flask import request, jsonify, g, Response
from flask.views import MethodView
import pymongo
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from pyquery import PyQuery as PQ
from exts import mongo, db
from models import LikeModel, CollectModel
from utils.log import Log
from utils.limit import Limiter


class LCAPI(MethodView):
    def get(self) -> Response:
        """
        param group 1:
            article_id[must]
            :return: 判断用户是否点赞关注
        param group 2:
            article_id[mustn't]
            page[optional]
            :return: 用户收藏列表
        """
        article_id: str = request.args.get('article_id')
        page: str = request.args.get('page', default='1')
        if article_id is not None:
            try:
                if ObjectId.is_valid(article_id):
                    article: dict = mongo.db.article.find_one({'_id': ObjectId(article_id)})  # TODO: type hint
                    if article is None:
                        return jsonify({'code': 404, 'message': "there's no such article"})
                    else:
                        if hasattr(g, 'user'):
                            user_id: str = g.user.user_id
                            like_obj: LikeModel = LikeModel.query.filter(and_(LikeModel.user_id == user_id,
                                                                              LikeModel.article_id == article_id)).first()
                            collect_obj: CollectModel = CollectModel.query.filter(and_(CollectModel.user_id == user_id,
                                                                                       CollectModel.article_id == article_id)).first()
                            return jsonify({'code': 200, 'message': 'success',
                                            'data': {
                                                'article': {'like': article['like'], 'collect': article['collect']},
                                                'user': {'like': bool(like_obj), 'collect': bool(collect_obj)}}})
                        else:
                            return jsonify({'code': 200, 'message': 'success',
                                            'data': {
                                                'article': {'like': article['like'], 'collect': article['collect']},
                                                'user': {'like': False, 'collect': False}}})
                else:
                    return jsonify({'code': 400, 'message': 'article_id invalid'})
            except SQLAlchemyError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
            except PyMongoError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
        else:
            if hasattr(g, 'user'):
                each_page: int = 10
                collect_lst: list[dict] = []
                article_id_lst: list[ObjectId] = []
                total_collect: int = CollectModel.query.filter(CollectModel.user_id == g.user.user_id).count()
                total_page: int = total_collect // each_page + 1 if total_collect % each_page else total_collect // each_page
                collects: list[CollectModel] = CollectModel.query.filter(CollectModel.user_id == g.user.user_id). \
                    offset(each_page * (int(page) - 1)).limit(each_page).all()
                for c in collects:
                    article_id_lst.append(ObjectId(c.article_id))
                collect_gen: pymongo.cursor.Cursor = mongo.db.article.find({'_id': {'$in': article_id_lst}},
                                                                           {'comment': 0})
                for c in collect_gen:
                    c['_id'] = str(c['_id'])
                    c['content'] = PQ(c['content']).text().replace('\n', '')[:180] + '. . . . . .'
                    collect_lst.append(c)
                return jsonify({'code': 200, 'message': 'success',
                                'data': {'current_page': page, 'total_collect': total_collect,
                                         'total_page': total_page, 'collect': collect_lst}})
            else:
                return jsonify({'code': 403, 'message': 'login required'})

    @Limiter('user')
    def put(self) -> Response:
        """
        param group 1:
            点赞
            like['1', '-1']
            collect['0']
            article_id[must]
            :return:
        param group 2:
            收藏
            like['0']
            collect['1', '-1']
            article_id[must]
            :return
        """
        like: str = str(request.form.get('like'))  # 0: 不改动 1: 点赞 -1: 取消点赞
        collect: str = str(request.form.get('collect'))  # 0: 不改动 1: 收藏 -1 : 取消收藏
        article_id: str = request.form.get('article_id')
        user_id: str = g.user.user_id
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
                like_obj: LikeModel = LikeModel.query. \
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
                        like_obj: LikeModel = LikeModel(article_id=article_id, user_id=user_id)
                        db.session.add(like_obj)
                        db.session.commit()
                        mongo.db.article.update_one({'_id': ObjectId(article_id)}, {'$inc': {'like': 1}})
                        return jsonify({'code': 200, 'message': 'success'})
                    elif like == '-1':
                        return jsonify({'code': 400, 'message': "You've canceled the like"})
            elif collect != '0':
                collect_obj: CollectModel = CollectModel.query. \
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
                        collect_obj: CollectModel = CollectModel(article_id=article_id, user_id=user_id)
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
            db.session.rollback()
            return jsonify({'code': 500, 'message': 'database error'})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})

