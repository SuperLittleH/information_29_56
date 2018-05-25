from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect

class Config(object):
    """配置文件的加载"""
    # 开启调试模式
    DEBUG = True
    # 配置Mysql数据库的连接信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/information_29'
    # 不追踪数据库的修改节省内存
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 配置redis数据库
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379


app = Flask(__name__)

# 获取配置信息
app.config.from_object(Config)

# 创建连接到mysql数据库的对象
db = SQLAlchemy(app)


# 创建连接到reids数据库对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

# 开启CSRF保护
CSRFProtect(app)

@app.route('/')
def index():
    # 测试redis数据库
    redis_store.set('name','itheima')

    return 'index'

if __name__ == '__main__':
    app.run()