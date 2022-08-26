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
# Usage

In this project we provide 5 main function to those who were graduated but didn't find a job so that they could get more information about how to find jobs in `China`.

url: [http://47.112.108.202/](http://47.112.108.202/)

1. job recommend

   We get more than 300000 jobs information and use these information to anlyse which job suits you.And provide comparison of horizontal and vertical.

2. plenty of article

   In this part, we provide some useful articles for you to read. 

3. resume

   In order to get a job, the first thing is to have a resume. So ...

4. forum

   You could provide your confusion or answer others questions. And if you were in dilemma, you could raise a vote to help yourself to do you'r decision.

5. chat

   This is not only a platform you could get jobs information, but also a community of graduates. So we think friends system should be built.

## 1. jobs recommend

> We get more than 300000 jobs information and use these information to anlyse which job suits you.And provide comparison of horizontal and vertical.

![image](https://user-images.githubusercontent.com/94276865/186970347-ada7a868-d97e-4353-b972-0c9a107cc5b6.png)

## 2. plenty of articles

![image](https://user-images.githubusercontent.com/94276865/186973929-1e7dfa91-b9cc-4dc9-8321-6034f2b6a380.png)

## 3. resume

>  In order to get a job, the first thing is to have a resume. So ...

![image](https://user-images.githubusercontent.com/94276865/186973558-86ae8f19-3cfb-4f16-a405-4fe378ee5af3.png)

## 4. forum

> You could provide your confusion or answer others questions. And if you were in dilemma, you could raise a vote to help yourself to do you'r decision.

![image](https://user-images.githubusercontent.com/94276865/186974139-73bd4d96-9c66-4af0-adb4-a368470c531b.png)

![image](https://user-images.githubusercontent.com/94276865/186974199-94f5357a-34f9-49b3-ac70-0d70b6e30f58.png)

## 5. chat

> This is not only a platform you could get jobs information, but also a community of graduates. So we think friends system should be built.

![image](https://user-images.githubusercontent.com/94276865/186974537-43be2f55-1e7d-4306-916b-c0e32e986ccf.png)