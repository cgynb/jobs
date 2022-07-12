from flask import Flask, g, request
from bps import user_bp
from utils.token_operation import validate_token, create_token
from exts import db, migrate, mail
from models import UserModel
import config


app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

app.register_blueprint(user_bp)


@app.before_request
def before_request():
    token, msg = validate_token(request.headers.get('Authorization'))
    # print('req', request.headers.get('Authorization'))
    if msg is None:
        try:
            user = UserModel.query.filter(UserModel.user_id == token.get('user_id')).first()
            g.user = user
        except Exception as e:
            print(e)


@app.after_request
def after_request(resp):
    if hasattr(g, 'user'):
        token = create_token(g.user)
        # print('resp', token)
        resp.headers['Authorization'] = token
    return resp


if __name__ == '__main__':
    app.run()
