from flask import jsonify, request, g
from flask.views import MethodView
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
import uuid
from exts import db
from models import VoteModel, TopicModel
from utils.limit import Limiter
from utils.log import Log
from utils.others import rand_str


class VoteAPI(MethodView):
    """
    post: 发起投票
    put: 进行投票
    """

    def get(self):
        topic_id = request.args.get('topic_id')
        page = int(request.args.get('page'))
        if topic_id is None:
            each_page = 10
            sql = """
                select 
                    topic_id, 
                    topic_content, 
                    op1, 
                    op2, 
                    op3, 
                    op4
                from topic
                limit :f, :t
            """
            topics = []
            topics_obj = db.session.execute(sql, params={'f': each_page * (page - 1), 't': each_page * page}).fetchall()
            for t in topics_obj:
                indexes = ('topic_id', 'topic_content', 'op1', 'op2', 'op3', 'op4',
                           'op1_count', 'op2_count', 'op3_count', 'op4_count')
                topic = dict(zip(indexes, t))
                topics.append(topic)
            return jsonify({'code': 200, 'message': 'success', 'data': {'votes': topics}})
        else:
            sql = """
                select 
                    topic.topic_id, 
                    topic.topic_content, 
                    topic.op1, 
                    topic.op2, 
                    topic.op3, 
                    topic.op4, 
                    (select count(1) 
                     from vote 
                     where topic_id = :topic_id and op = 1),
                    (select count(1) 
                     from vote 
                     where topic_id = :topic_id and op = 2),
                    (select count(1) 
                     from vote 
                     where topic_id = :topic_id and op = 3),
                    (select count(1) 
                     from vote 
                     where topic_id = :topic_id and op = 4)
                from topic
                where topic.topic_id = :topic_id
            """
            topic = db.session.execute(sql, params={'topic_id': topic_id}).fetchone()
            indexes = ('topic_id', 'topic_content', 'op1', 'op2', 'op3', 'op4',
                       'op1_count', 'op2_count', 'op3_count', 'op4_count')
            topic = dict(zip(indexes, topic))
            topic['options'] = list()
            topic['options'].append({'name': topic.pop('op1'), 'count': topic.pop('op1_count')})
            topic['options'].append({'name': topic.pop('op2'), 'count': topic.pop('op2_count')})
            topic['options'].append({'name': topic.pop('op3'), 'count': topic.pop('op3_count')})
            topic['options'].append({'name': topic.pop('op4'), 'count': topic.pop('op4_count')})
            topic['choose'] = None
            if hasattr(g, 'user'):
                v = VoteModel.query.\
                    filter(and_(VoteModel.topic_id == topic_id, VoteModel.user_id == g.user.user_id)).first()
                topic['choose'] = topic['options'][v.op - 1]['name']
            return jsonify({'code': 200, 'message': 'success', 'data': topic})

    @Limiter('user')
    def post(self):
        topic_content = request.form.get('topic_content')
        op1 = request.form.get('op1')
        op2 = request.form.get('op2')
        op3 = request.form.get('op3')
        op4 = request.form.get('op4')
        topic_id = 'topic-' + rand_str(6) + '-' + str(uuid.uuid4())
        try:
            topic = TopicModel(topic_id=topic_id, topic_content=topic_content, op1=op1, op2=op2, op3=op3, op4=op4)
            db.session.add(topic)
            db.session.commit()
        except SQLAlchemyError as e:
            Log.error(e)
            db.session.rollback()
            return jsonify({'code': 500, 'message': 'database error'})
        return jsonify({'code': 200, 'message': 'success',
                        'data': {
                            'topic_content': topic_content,
                            'topic_id': topic_id,
                            'options': {
                                'op1': op1,
                                'op2': op2,
                                'op3': op3,
                                'op4': op4
                            }
                        }})

    @Limiter('user')
    def put(self):
        topic_id = request.form.get('topic_id')
        op = request.form.get('op')
        if op is None:
            return jsonify({'code': 400, 'message': 'params error (need op)'})
        elif op is not None:
            if op not in ('1', '2', '3', '4'):
                return jsonify({'code': 400, 'message': "params error (op must in ('1', '2', '3', '4'))"})
        if topic_id is None:
            return jsonify({'code': 400, 'message': 'params error (need topic_id)'})
        elif topic_id is not None:
            v = TopicModel.query.filter(TopicModel.topic_id == topic_id).first()
            if v is None:
                return jsonify({'code': 404, 'message': f"there's no such topic (topic_id: {topic_id})"})
            v = VoteModel.query. \
                filter(
                    and_(
                        VoteModel.topic_id == topic_id,
                        VoteModel.user_id == g.user.user_id
                    )
                ).first()
            if v is not None:
                return jsonify({'code': 403, 'message': "you have voted"})
        try:
            vote = VoteModel(topic_id=topic_id, user_id=g.user.user_id, op=op)
            db.session.add(vote)
            db.session.commit()
        except SQLAlchemyError as e:
            Log.error(e)
            db.session.rollback()
            return jsonify({'code': 500, 'message': 'database error'})
        return jsonify({'code': 200, 'message': 'success'})
