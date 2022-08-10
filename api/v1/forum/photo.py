from flask import request, jsonify, Response, g
from flask.views import MethodView
from utils.user_info import upload_photo
from utils.limit import Limiter
import os
import uuid


class PhotoAPI(MethodView):
    @Limiter('user')
    def post(self):
        photo = request.files.get('photo')
        filename, suffix = os.path.splitext(photo.filename)
        upload_photo(photo_obj=photo,
                     suffix=suffix,
                     photo_name='forum-' + str(uuid.uuid4()) + '-' + g.user.user_id + '-' + filename)
        return jsonify({'code': 200, 'message': 'success'})
