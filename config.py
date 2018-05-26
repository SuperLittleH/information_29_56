from redis import StrictRedis
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