import typing as t
from flask import request, jsonify, Blueprint, Response
from flask.views import MethodView
import pymongo
from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from pyquery import PyQuery as PQ
from exts import mongo
from models import UserModel
from utils.log import Log
from utils.user_info import obj_to_dict


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
                    a['content'] = PQ(a['content']).text().replace('\n', '')[:220] + '. . . . . .'
                    article_lst.append(a)
                return jsonify({'code': 200, 'message': 'success',
                                'data': {'current_page': page, 'total_article': total_article,
                                         'total_page': total_page, 'article': article_lst}})
            else:  # 获取一篇文章信息
                if ObjectId.is_valid(article_id):
                    article: t.Mapping[
                        str,
                        t.Union[
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
                        ]
                    ] = mongo.db.article.find_one({'_id': ObjectId(article_id)})
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