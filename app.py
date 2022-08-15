from flask import Flask, g, request, Response
import click
from sqlalchemy.exc import SQLAlchemyError
from api import api_bp
from utils.token_operation import validate_token, create_token
from exts import db, migrate, mail, cors, mongo, socketio
from models import UserModel
from chat import ChatNamespace
import toml
import logging
from utils.log import Log


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
socketio.init_app(app, cors_allowed_origins='*')

socketio.on_namespace(ChatNamespace('/chat'))

app.register_blueprint(api_bp)


@app.before_request
def before_request():
    token, msg = validate_token(request.headers.get('Authorization'))
    if msg is None:
        try:
            user = UserModel.query.filter(UserModel.user_id == token.get('user_id')).first()
            g.user = user
        except SQLAlchemyError as e:
            Log.error(e)
    elif msg == 'token已失效':
        g.refresh = True


@app.after_request
def after_request(resp) -> Response:
    if hasattr(g, 'refresh') and g.refresh is True:
        resp.headers['Authorization'] = 'refresh'
    if hasattr(g, 'user'):
        resp.headers['Authorization'] = create_token(g.user)
        if hasattr(g, 'login') and g.login is True:
            resp.headers['refresh-token'] = create_token(g.user, refresh_token=True)
    return resp


@app.cli.command('start')
@click.option('--port', type=int, default=5000, help='running port')
def run(port):
    import eventlet
    from eventlet import wsgi
    eventlet.monkey_patch()
    wsgi.server(eventlet.listen(('0.0.0.0', port)), app)


@app.route('/chatroom/')
def c():
    print(request.method)
    from flask import render_template
    return render_template('chat.html', async_mode=socketio.async_mode)


if __name__ == '__main__':
    socketio.run(app, '0.0.0.0', 5000, debug=True)
