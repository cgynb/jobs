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
        topic['options'].append({'op1': topic.pop('op1'), 'count': topic.pop('op1_count')})
        topic['options'].append({'op2': topic.pop('op2'), 'count': topic.pop('op2_count')})
        topic['options'].append({'op3': topic.pop('op3'), 'count': topic.pop('op3_count')})
        topic['options'].append({'op4': topic.pop('op4'), 'count': topic.pop('op4_count')})
        if hasattr(g, 'user'):
            v = VoteModel.query.\
                filter(and_(VoteModel.topic_id == topic_id, VoteModel.user_id == g.user.user_id)).first()
            for i, data in enumerate(topic['options'], start=1):
                topic['options'][i-1]['choose'] = (v.op == i)
        else:
            for i, data in enumerate(topic['options'], start=1):
                topic['options'][i-1]['choose'] = False
        return jsonify({'code': 200, 'message': 'success', 'data': topic})

    @Limiter('user')
    def post(self):
        topic_content = request.form.get('topic_content')
        op1 = request.form.get('op1')
        op2 = request.form.get('op2')
        op3 = request.form.get('op3')
        op4 = request.form.get('op4')
        topic_id = 'topic-' + rand_str(6) + '-' + str(uuid.uuid4())
        topic = TopicModel(topic_id=topic_id, topic_content=topic_content, op1=op1, op2=op2, op3=op3, op4=op4)
        db.session.add(topic)
        db.session.commit()
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
            return jsonify({'code': 500, 'message': 'database error'})
        return jsonify({'code': 200, 'message': 'success'})
