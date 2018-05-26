from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import Config


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