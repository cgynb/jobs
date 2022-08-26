from flask import request, jsonify
from flask.views import MethodView
from models import JobsModel
from objprint import op
import ast


class LibraryAPI(MethodView):
    def get(self):
        each_page = 20
        page = int(request.args.get('page', default='1'))
        jbs = JobsModel.query.filter().offset(each_page * (int(page) - 1)).limit(each_page).all()
        has_company = list()
        hasnt_company = list()
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
