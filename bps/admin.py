from flask import Blueprint
from utils.role_limit import login_required

bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')


@bp.route('/log/', methods=['GET'])
@login_required
def log():
    with open('./app.log', 'r', encoding='utf-8') as log_file:
        log_str = ''
        lines = log_file.readlines()
        for s in lines:
            log_str += f"<p>{s}</p>"
    return log_str
