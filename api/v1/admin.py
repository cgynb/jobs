from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/log/', methods=['GET'])
def log():
    with open('./app.log', 'r', encoding='utf-8') as log_file:
        log_str = ''
        lines = log_file.readlines()
        for s in lines:
            log_str += f"<p>{s}</p>"
    return log_str
