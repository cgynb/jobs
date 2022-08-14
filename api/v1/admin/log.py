from flask import jsonify
from flask.views import MethodView


class LogAPI(MethodView):
    def get(self):
        with open('app.log') as f:
            log = f.readlines()
        log = list(map(lambda x: "<p>" + x + "</p>", log))
        # return jsonify({'code': 200, 'message': 'success',
        #                 'data': {
        #                     'log': log
        #                 }})
        return ''.join(log)
