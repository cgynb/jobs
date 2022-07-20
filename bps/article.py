from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
import time
from pyquery import PyQuery as PQ
from exts import mongo, db
from models import LikeModel, CollectModel, UserModel
from utils.log import Log
from utils.role_limit import login_required
from utils.user_info import user_dict, obj_to_dict

bp = Blueprint('article', __name__, url_prefix='/api/v1/article')


class ArticleAPI(MethodView):
    def get(self):  # 1. article_id[必选] -> 文章信息         2. page[可选|None] type[可选|None] article_id[None] 返回文章列表
        article_id = request.args.get('article_id')
        page = request.args.get('page', default='1')
        article_type = request.args.get('type')
        try:
            if article_id is None:  # 获取文章列表
                if article_type is None:
                    condition = {}
                else:
                    condition = {'type': article_type}
                each_page = 10
                total_article = mongo.db.article.count_documents(condition)
                total_page = total_article // each_page + 1 if total_article % each_page else total_article // each_page
                articles = mongo.db.article.find(condition, {'comment': 0}). \
                    limit(each_page).skip((int(page) - 1) * 10)
                article_lst = []
                for a in articles:
                    a['_id'] = str(a['_id'])
                    a['content'] = PQ(a['content']).text().replace('\n', '')[:100]
                    article_lst.append(a)
                return jsonify({'code': 200, 'message': 'success',
                                'data': {'current_page': page, 'total_article': total_article,
                                         'total_page': total_page, 'article': article_lst}})
            else:  # 获取一篇文章信息
                if ObjectId.is_valid(article_id):
                    article = mongo.db.article.find_one({'_id': ObjectId(article_id)})
                    if article is None:
                        return jsonify({'code': 404, 'message': "there's no such article"})
                    article['_id'] = str(article['_id'])
                    user_id_dict = dict()  # id到用户详细关系的映射 {id1: userinfo1, id2: userinfo2 ...}
                    # 第一个遍历获取到所有的user_id
                    for i in range(len(article['comment'])):
                        user_id = article['comment'][i]['comment_id'].split('-')[1]
                        send_time = article['comment'][i]['comment_id'].split('-')[2]
                        user_id_dict[user_id] = None
                        article['comment'][i]['send_time'] = send_time
                        for ii in range(len(article['comment'][i]['subcomment'])):
                            user_id = article['comment'][i]['subcomment'][ii]['subcomment_id'].split('-')[1]
                            send_time = article['comment'][i]['subcomment'][ii]['subcomment_id'].split('-')[2]
                            user_id_dict[user_id] = None
                            article['comment'][i]['subcomment'][ii]['send_time'] = send_time

                    # 从数据库中拿到评论中所有id
                    user_obj_lst = UserModel.query.filter(UserModel.user_id.in_(user_id_dict.keys())).all()
                    # 将user_id_dict的每个id对应info
                    for key in user_id_dict.keys():
                        for u in user_obj_lst:
                            user_id_dict[key] = obj_to_dict(u)
                    # 第二次循环将info并入返回值
                    for i in range(len(article['comment'])):
                        user_id = article['comment'][i]['comment_id'].split('-')[1]
                        article['comment'][i] |= user_id_dict[user_id]
                        for ii in range(len(article['comment'][i]['subcomment'])):
                            user_id = article['comment'][i]['subcomment'][ii]['subcomment_id'].split('-')[1]
                            article['comment'][i]['subcomment'][ii] |= user_id_dict[user_id]
                    return jsonify({'code': 200, 'message': 'success', 'data': article})
                else:
                    return jsonify({'code': 400, 'message': 'article_id invalid'})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})

    @login_required
    def post(self):
        article_id = request.form.get('article_id')
        user_id = g.user.user_id
        comment = request.form.get('comment', default=None)
        comment_id = request.form.get('comment_id', default=None)
        subcomment = request.form.get('subcomment', default=None)
        if ObjectId.is_valid(article_id):
            try:
                article = mongo.db.article.find_one({'_id': ObjectId(article_id)}, {'comment': 1})
                if article is None:
                    return jsonify({'code': 404, 'message': "there's no such article"})
                else:
                    if comment is not None:  # 添加评论
                        if len(comment.strip()) == 0:
                            return jsonify({'code': 400, 'message': "there's nothing in the comment"})
                        else:
                            comment_id = 'comment' + '-' + user_id + '-' + str(int(time.time()))
                            mongo.db.article.update_one(
                                {'_id': ObjectId(article_id)},  # 条件
                                {'$addToSet': {
                                    'comment': {'comment_id': comment_id, 'comment': comment, 'subcomment': []}}})
                            return jsonify({'code': 200, 'message': 'success',
                                            'data': {'comment_id': comment_id,
                                                     'comment': comment} | user_dict(user_id)})
                    elif subcomment is not None and comment_id is not None:  # 添加子评论
                        if len(subcomment.strip()) == 0:
                            return jsonify({'code': 400, 'message': "there's nothing in the subcomment"})
                        else:
                            subcomment_id = 'subcomment' + '-' + user_id + '-' + str(int(time.time()))
                            index = -1
                            for cnt, cmt in enumerate(article['comment']):
                                if cmt['comment_id'] == comment_id:
                                    index = cnt
                                    break
                            if index == -1:
                                return jsonify({'code': 404, 'message': "there's no such comment to reply"})
                            article['comment'][index]['subcomment'].append(
                                {'subcomment': subcomment, 'subcomment_id': subcomment_id})
                            mongo.db.article.update_one({'_id': ObjectId(article_id)},
                                                        {'$set': {'comment': article['comment']}})
                            return jsonify({'code': 200, 'message': 'success',
                                            'data': {'comment_id': comment_id, 'subcomment_id': subcomment_id,
                                                     'subcomment': subcomment} | user_dict(user_id)})
                    else:
                        jsonify({'code': 400, 'message': 'params error'})
            except PyMongoError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
        else:
            return jsonify({'code': 400, 'message': 'article_id invalid'})


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
                        like_obj = LikeModel.query.filter(and_(LikeModel.user_id == user_id,
                                                               LikeModel.article_id == article_id)).first()
                        collect_obj = CollectModel.query.filter(and_(CollectModel.user_id == user_id,
                                                                     CollectModel.article_id == article_id)).first()
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
