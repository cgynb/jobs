<Rule '/api/v1/article/recommend/' (GET, HEAD, OPTIONS) -> api.v1.article.recommend>,
 
<Rule '/api/v1/article/comment/' (OPTIONS, POST) -> api.v1.article.comment>,
 
<Rule '/api/v1/article/lc/' (GET, PUT, HEAD, OPTIONS) -> api.v1.article.lc>,
  
<Rule '/api/v1/article/' (GET, HEAD, OPTIONS) -> api.v1.article.>,
 
<Rule '/api/v1/forum/question/' (GET, HEAD, OPTIONS, POST) -> api.v1.forum.question>,
 
<Rule '/api/v1/forum/answer/' (GET, HEAD, OPTIONS, POST) -> api.v1.forum.answer>,
 
<Rule '/api/v1/admin/log/' (GET, HEAD, OPTIONS) -> api.v1.admin.log>,
 
<Rule '/api/v1/user/refresh/' (OPTIONS, POST) -> api.v1.user.refresh>,
 
<Rule '/api/v1/user/captcha/' (GET, HEAD, OPTIONS, POST) -> api.v1.user.captcha>,
 
<Rule '/api/v1/user/login/' (OPTIONS, POST) -> api.v1.user.login>,

<Rule '/api/v1/user/' (PUT, OPTIONS, POST) -> api.v1.user.user>,
