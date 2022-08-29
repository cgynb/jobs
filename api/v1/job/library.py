from flask import jsonify, Response
from flask.views import MethodView
import random
from models import JobsModel
import ast


class LibraryAPI(MethodView):
    def get(self) -> Response:
        each_page: int = 20
        # page: int = int(request.args.get('page', default='1'))
        # jbs: list = JobsModel.query.filter().offset(each_page * (int(page) - 1)).limit(each_page).all()
        # jbs: list = JobsModel.query.filter().order_by(func.rand()).limit(each_page).all()
        jbs = [JobsModel.query.filter(JobsModel.id == random.randint(1, 333076)).first() for _ in range(each_page)]
        has_company: list = list()
        hasnt_company: list = list()
        for jb in jbs:
            if jb.company:
                has_company.append({
                    'number': jb.number,
                    'job': jb.job,
                    'city': jb.city,
                    'salary': jb.salary,
                    'education': jb.education,
                    'experience': jb.experience,
                    'goodList': ast.literal_eval(jb.goodList),
                    'needList': ast.literal_eval(jb.needList),
                    'jobInfo': jb.jobInfo,
                    'company': jb.company,
                    "companyType": jb.companyType,
                    "companyPeople": jb.companyPeople,
                    "companyPosition": jb.companyPosition,
                    "companyInfo": jb.companyInfo
                })
            else:
                hasnt_company.append({
                    'number': jb.number,
                    'job': jb.job,
                    'city': jb.city,
                    'salary': jb.salary,
                    'education': jb.education,
                    'experience': jb.experience,
                    'goodList': ast.literal_eval(jb.goodList),
                    'needList': ast.literal_eval(jb.needList),
                    'jobInfo': jb.jobInfo,
                    'company': None,
                    "companyType": None,
                    "companyPeople": None,
                    "companyPosition": None,
                    "companyInfo": None
                })
        return jsonify({'code': 200, 'message': 'success',
                        'data': {
                                'has_company': has_company,
                                'hasnt_company': hasnt_company
                            }})
