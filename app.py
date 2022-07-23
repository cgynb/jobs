import os
from flask import Flask, g, request
from bps import user_bp, article_bp, admin_bp
from utils.token_operation import validate_token, create_token
from exts import db, migrate, mail, cors, mongo
from models import UserModel
import toml
import logging
from utils.user_info import upload_avatar

app = Flask(__name__)
app.config.from_file('config.toml', load=toml.load)

handler = logging.FileHandler('app.log', encoding='UTF-8')
logging_format = logging.Formatter('\n===============================================================================\n'
                                   '%(asctime)s - %(levelname)s - %(filename)s - '
                                   '%(funcName)s - %(lineno)s - (ip: %(message)s)')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)

db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)
cors.init_app(app, supports_credentials=True, expose_headers=['Authorization', 'refresh-token'])
mongo.init_app(app)

app.register_blueprint(user_bp)
app.register_blueprint(article_bp)
app.register_blueprint(admin_bp)


@app.before_request
def before_request():
    token, msg = validate_token(request.headers.get('Authorization'))
    if msg is None:
        try:
            user = UserModel.query.filter(UserModel.user_id == token.get('user_id')).first()
            g.user = user
        except Exception as e:
            print(e)
    elif msg == 'token已失效':
        g.refresh = True


@app.after_request
def after_request(resp):
    if hasattr(g, 'refresh') and g.refresh is True:
        resp.headers['Authorization'] = 'refresh'
    if hasattr(g, 'user'):
        resp.headers['Authorization'] = create_token(g.user)
        if hasattr(g, 'login') and g.login is True:
            resp.headers['refresh-token'] = create_token(g.user, refresh_token=True)
    return resp


@app.route('/', methods=['POST'])
def test_view():
    f = request.files.get('avatar')
    suffix = os.path.splitext(f.filename)[-1]
    user_id = '123'
    upload_avatar(user_id, f, suffix)
    return 'test'


if __name__ == '__main__':
    app.run('0.0.0.0')
