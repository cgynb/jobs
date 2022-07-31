import typing as t
from flask import Blueprint, request, jsonify, g, Response
from flask.views import MethodView
import pymongo
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
from ai_package.recommend import recommend_ids

bp = Blueprint('article', __name__, url_prefix='/article')


# TODO: POST ARTICLE
class ArticleAPI(MethodView):
    def get(self) -> Response:
        """
        param group 1:
            article_id[must]
            page[useless]
            type[useless]
            :return: 文章信息
        param group 2:
            page[optional]
            type[optional]
            article_id[mustn't]
            :return: 文章列表
        """
        article_id: t.Optional[str] = request.args.get('article_id')

        page: str = request.args.get('page', default='1')
        article_type: t.Optional[str] = request.args.get('type')
        try:
            if article_id is None:  # 获取文章列表
                if article_type is None:
                    condition: t.Mapping[str, t.Union[str, int]] = dict()
                else:
                    condition: t.Mapping[str, t.Union[str, int]] = {'type': article_type}
                each_page: int = 10
                total_article: int = mongo.db.article.count_documents(condition)
                total_page: int = total_article // each_page + 1 if total_article % each_page else total_article // each_page
                articles: pymongo.cursor.Cursor = mongo.db.article.find(condition, {'comment': 0}). \
                    limit(each_page).skip((int(page) - 1) * 10)
                article_lst: list[
                    t.Mapping[
                        str,
                        t.Union[int, str]
                    ]
                ] = []
                for a in articles:
                    a['_id'] = str(a['_id'])
                    a['content'] = PQ(a['content']).text().replace('\n', '')[:100] + '. . . . . .'
                    article_lst.append(a)
                return jsonify({'code': 200, 'message': 'success',
                                'data': {'current_page': page, 'total_article': total_article,
                                         'total_page': total_page, 'article': article_lst}})
            else:  # 获取一篇文章信息
                if ObjectId.is_valid(article_id):
                    article: t.Mapping[
                        str,
                        int,
                        list[
                            t.Mapping[
                                str,
                                list[
                                    t.Mapping[
                                        str,
                                        str
                                    ]
                                ]
                            ]
                        ]
                    ] = mongo.db.article.find_one({'_id': ObjectId(article_id)})
                    from pprint import pprint
                    pprint(article)
                    if article is None:
                        return jsonify({'code': 404, 'message': "there's no such article"})
                    article['_id'] = str(article['_id'])
                    # id到用户详细关系的映射表user_id_dict =  {id1: userinfo1, id2: userinfo2 ...}
                    user_id_dict: t.Mapping[str, t.Optional[t.Mapping[str, t.Union[str, list]]]] = dict()
                    # 第一个遍历获取到所有的user_id
                    for i in range(len(article['comment'])):
                        user_id: str = article['comment'][i]['comment_id'].split('-')[1]
                        send_time: str = article['comment'][i]['comment_id'].split('-')[2]
                        user_id_dict[user_id] = None
                        article['comment'][i]['send_time'] = send_time
                        for ii in range(len(article['comment'][i]['subcomment'])):
                            user_id: str = article['comment'][i]['subcomment'][ii]['subcomment_id'].split('-')[1]
                            send_time: str = article['comment'][i]['subcomment'][ii]['subcomment_id'].split('-')[2]
                            user_id_dict[user_id] = None
                            article['comment'][i]['subcomment'][ii]['send_time'] = send_time
                    # 从数据库中拿到评论中所有id
                    user_obj_lst: list[UserModel] = UserModel.query. \
                        filter(UserModel.user_id.in_(user_id_dict.keys())).all()
                    # 将user_id_dict的每个id对应info
                    for key in user_id_dict.keys():
                        for u in user_obj_lst:
                            if key == u.user_id:
                                user_id_dict[key] = obj_to_dict(u)
                    # 第二次循环将info并入返回值
                    for i in range(len(article['comment'])):
                        user_id: str = article['comment'][i]['comment_id'].split('-')[1]
                        article['comment'][i] |= user_id_dict[user_id]
                        for ii in range(len(article['comment'][i]['subcomment'])):
                            user_id: str = article['comment'][i]['subcomment'][ii]['subcomment_id'].split('-')[1]
                            article['comment'][i]['subcomment'][ii] |= user_id_dict[user_id]
                    return jsonify({'code': 200, 'message': 'success', 'data': article})
                else:
                    return jsonify({'code': 400, 'message': 'article_id invalid'})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})
        except ValueError as e:
            Log.error(e)
            return jsonify({'code': 400, 'message': f'params error: {request.args.to_dict()}'})


# TODO: DELETE ARTICLE COMMENT
class CommentAPI(MethodView):
    @login_required
    def post(self) -> Response:
        """
        param group 1:
            发送评论
            article_id[must]
            comment[must]
            comment_id[useless]
            subcomment[useless]
            :return: 发送的那条评论的信息
        param group 2:
            发送子评论
            article_id[must]
            comment[mustn't]
            comment_id[must]
            subcomment[must]
            :return: 发送的子评论的信息
        """
        article_id: str = request.form.get('article_id')
        user_id: str = g.user.user_id
        comment: t.Optional[str] = request.form.get('comment', default=None)
        comment_id: t.Optional[str] = request.form.get('comment_id', default=None)
        subcomment: t.Optional[str] = request.form.get('subcomment', default=None)
        if ObjectId.is_valid(article_id):
            try:
                article: t.Mapping[str,
                                   t.Union[
                                       ObjectId,
                                       list[
                                           t.Mapping[
                                               str,
                                               t.Union[
                                                   str,
                                                   list[t.Mapping[str, str]]
                                               ]
                                           ]
                                       ]
                                   ]
                ] = mongo.db.article.find_one({'_id': ObjectId(article_id)}, {'comment': 1})
                if article is None:
                    return jsonify({'code': 404, 'message': "there's no such article"})
                else:
                    if comment is not None:  # 添加评论
                        if len(comment.strip()) == 0:
                            return jsonify({'code': 400, 'message': "there's nothing in the comment"})
                        else:
                            send_time: str = str(int(time.time()))
                            comment_id: str = 'comment' + '-' + user_id + '-' + send_time
                            mongo.db.article.update_one(
                                {'_id': ObjectId(article_id)},  # 条件
                                {'$addToSet': {
                                    'comment': {'comment_id': comment_id, 'comment': comment, 'subcomment': []}
                                }})
                            return jsonify({'code': 200, 'message': 'success',
                                            'data': {'comment_id': comment_id,
                                                     'comment': comment,
                                                     'send_time': send_time,
                                                     'subcomment': []} | user_dict(user_id)})
                    elif subcomment is not None and comment_id is not None:  # 添加子评论
                        if len(subcomment.strip()) == 0:
                            return jsonify({'code': 400, 'message': "there's nothing in the subcomment"})
                        else:
                            send_time: str = str(int(time.time()))
                            subcomment_id: str = 'subcomment' + '-' + user_id + '-' + send_time
                            index: int = -1
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
                                            'data': {'comment_id': comment_id,
                                                     'subcomment_id': subcomment_id,
                                                     'subcomment': subcomment,
                                                     'send_time': send_time} | user_dict(user_id)})
                    else:
                        jsonify({'code': 400, 'message': 'params error'})
            except PyMongoError as e:
                Log.error(e)
                return jsonify({'code': 500, 'message': 'database error'})
        else:
            return jsonify({'code': 400, 'message': 'article_id invalid'})


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


# like and collect
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
                    c['content'] = PQ(c['content']).text().replace('\n', '')[:50] + '. . . . . .'
                    collect_lst.append(c)
                return jsonify({'code': 200, 'message': 'success',
                                'data': {'current_page': page, 'total_collect': total_collect,
                                         'total_page': total_page, 'collect': collect_lst}})
            else:
                return jsonify({'code': 403, 'message': 'login required'})

    @login_required
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
            return jsonify({'code': 500, 'message': 'database error'})
        except PyMongoError as e:
            Log.error(e)
            return jsonify({'code': 500, 'message': 'database error'})
