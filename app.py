from flask import Flask, g, request
from bps import user_bp, article_bp
from utils.token_operation import validate_token, create_token
from exts import db, migrate, mail, cors, mongo
from models import UserModel
import toml


app = Flask(__name__)
app.config.from_file('config.toml', load=toml.load)

db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)
cors.init_app(app, supports_credentials=True, expose_headers=['Authorization', 'refresh-token'])
mongo.init_app(app, 'mongodb://localhost:27017/jobs')

app.register_blueprint(user_bp)
app.register_blueprint(article_bp)


@app.before_request
def before_request():
    token, msg = validate_token(request.headers.get('Authorization'))
    # print(token, msg, request.headers.get('Authorization'))
    if msg is None:
        try:
            user = UserModel.query.filter(UserModel.user_id == token.get('user_id')).first()
            g.user = user
        except Exception as e:
            print(e)


@app.after_request
def after_request(resp):
    if hasattr(g, 'user'):
        resp.headers['Authorization'] = create_token(g.user)
        if hasattr(g, 'login') and g.login is True:
            resp.headers['refresh-token'] = create_token(g.user, refresh_token=True)
    # print(resp.headers['Authorization'])
    return resp


if __name__ == '__main__':
    app.run('0.0.0.0')
