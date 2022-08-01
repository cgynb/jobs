<Rule '/api/v1/article/recommend/' (OPTIONS, GET, HEAD) -> api.v1.article.recommend>
 
<Rule '/api/v1/article/comment/' (OPTIONS, POST) -> api.v1.article.comment>

<Rule '/api/v1/article/lc/' (PUT, OPTIONS, GET, HEAD) -> api.v1.article.like-collect>

<Rule '/api/v1/forum/question/' (OPTIONS, POST, GET, HEAD) -> api.v1.forum.question>

<Rule '/api/v1/forum/answer/' (OPTIONS, GET, DELETE, POST, HEAD) -> api.v1.forum.answer>

<Rule '/api/v1/user/refresh/' (OPTIONS, POST) -> api.v1.user.refresh>
 
<Rule '/api/v1/user/captcha/' (OPTIONS, POST, GET, HEAD) -> api.v1.user.captcha>

<Rule '/api/v1/user/login/' (OPTIONS, POST) -> api.v1.user.login>

<Rule '/api/v1/article/' (OPTIONS, GET, HEAD) -> api.v1.article.article>

<Rule '/api/v1/user/' (PUT, OPTIONS, POST) -> api.v1.user.user>

```python
var = {
    'str': 12,
    'str': [
        {
            'str': [
                {'str': 'str'}
            ]
        }
    ]
}
```
