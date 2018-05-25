from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

class Config(object):
    """配置文件的加载"""
    # 项目秘钥
    SECRET_KEY = 'q7pBNcWPgmF6BqB6b5VICF7z7pI+90o0O4CaJsFGjzRsYiya9SEgUDytXvzFsIaR'

    # 开启调试模式
    DEBUG = True
    # 配置Mysql数据库的连接信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/information_29'
    # 不追踪数据库的修改节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 配置redis数据库
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 指定session用什么存储
    SESSION_TYPE = 'redis'
    # 指定session数据存储在后端的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 是否使用secret_key签名你的session
    SESSION_USE_SIGNER = True
    #设置过期时间,要求SESSION_PERMANENT,True,默认是31天
    PERMSNENT_SESSIPN_LIFETIME = 60*60*24 #一天有效期



app = Flask(__name__)

# 获取配置信息
app.config.from_object(Config)

# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)


# 创建连接到reids数据库对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

# 开启CSRF保护
CSRFProtect(app)

# 指定session数据存储在后端的位置
Session(app)

@app.route('/')
def index():
    # 测试redis数据库
    # redis_store.set('name','itheima')

    # 测试session
    from flask import session
    # 会将('age':'2')写入cookie
    session['age'] = '2'

    return 'index'

if __name__ == '__main__':
    app.run()