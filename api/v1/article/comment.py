import typing as t
from flask import request, jsonify, g, Response
from flask.views import MethodView
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
import time
from exts import mongo
from utils.log import Log
from utils.limit import Limiter
from utils.user_info import user_dict


# TODO: DELETE ARTICLE COMMENT
class CommentAPI(MethodView):
    @Limiter('speaker')
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
