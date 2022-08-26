# jobs
[![Flask](https://img.shields.io/badge/Flask-2.2.2-blue)](https://github.com/cgynb/jobs)
[![Python](https://img.shields.io/badge/python-3.9%20%7C%203.10-blue)](https://img.shields.io/badge/python-3.9%20%7C%203.10-blue)

a back end of a platform called 毕业剩转圈圈

# Startup this project

1. activate your virtual environment
2. use `pip install -r package.txt` command
3. paste these code into `flask-socketio/__init__.py`
    ```python
    def participants(room=None, namespace=None):
        socketio = flask.current_app.extensions['socketio']
        namespace = namespace or flask.request.namespace
        return [sid for sid, _ in socketio.server.manager.get_participants(namespace, room)]
    ```
4. use `flask start --port {port}` or `python app.py (default port is 5000)` to start the project

success: 

```cmd
(venv) > flask start --port 5000
(16528) wsgi starting up on http://0.0.0.0:5000
```
![image](https://user-images.githubusercontent.com/94276865/186970347-ada7a868-d97e-4353-b972-0c9a107cc5b6.png)
