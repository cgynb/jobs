JSON_AS_ASCII = False

# 数据库
USERNAME = 'root'
PASSWORD = 'Cgy005688'
HOST = 'sh-cynosdbmysql-grp-kuvfpbfg.sql.tencentcdb.com'
PORT = '25736'
DATABASE = 'jobs'

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".\
    format(USERNAME, PASSWORD, HOST, PORT, DATABASE)


# 便于调试
TEMPLATES_AUTO_RELOAD = True
SEND_FILE_MAX_AGE_DEFAULT = 0
SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = 'hhhhhhhh'
SALT = 'jjjj'

# 邮箱配置
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEBUG = True
MAIL_USERNAME = '948628463@qq.com'
MAIL_PASSWORD = 'asjgvyfmrgbtbbij'
MAIL_DEFAULT_SENDER = '948628463@qq.com'
