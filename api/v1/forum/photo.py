from flask import request, jsonify, Response, g
from flask.views import MethodView
from utils.user_info import upload_photo
from utils.limit import Limiter
import os
import uuid


class PhotoAPI(MethodView):
    @Limiter('user')
    def post(self) -> Response:
        photo = request.files.get('photo')
        filename, suffix = os.path.splitext(photo.filename)
        file_name: str = 'forum-' + str(uuid.uuid4()) + '-' + g.user.user_id + '-' + filename
        file_url: str = 'https://byszqq-1310478750.cos.ap-nanjing.myqcloud.com/' + file_name + suffix
        upload_photo(photo_obj=photo,
                     suffix=suffix,
                     photo_name=file_name)
        return jsonify({'code': 200, 'message': 'success',
                        'data': {
                            'url': file_url
                        }})
