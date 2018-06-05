from flask import Flask,g,render_template
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_session import Session
# from config import Config,DevlopmentConfig,ProductionConfig,UnittestConfig
from config import configs
import logging
from logging.handlers import RotatingFileHandler




def setup_log(level):
    """根据创建app时的配置环境，加载日志等级"""
    # 设置⽇日志的记录等级
    logging.basicConfig(level=level)
    # 调试debug级 # 创建⽇日志记录器器，指明⽇日志保存的路路径、每个⽇日志⽂文件的最⼤大⼤大⼩小、保存的⽇日志⽂文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    #  创建⽇日志记录的格式                 ⽇日志等级    输⼊入⽇日志信息的⽂文件名 ⾏行行数    ⽇日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    #  为刚创建的⽇日志记录器器设置⽇日志记录格式
    file_log_handler.setFormatter(formatter)
    #  为全局的⽇日志⼯工具对象（flask app使⽤用的）添加⽇日志记录器器
    logging.getLogger().addHandler(file_log_handler)

# 创建SQLAlchemy对象
db = SQLAlchemy()
redis_store = None

def create_app(config_name):
    # 根据创建app时的配置环境，加载日志等级
    setup_log(configs[config_name].LEVEL_LOG)

    app = Flask(__name__)

    # 获取配置信息
    app.config.from_object(configs[config_name])

    db.init_app(app)

    # 创建连接到reids数据库对象
    global redis_store
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT,decode_responses=True)


    # 开启CSRF保护
    CSRFProtect(app)

    # 使用请求钩子实现每个相应中写入cookie
    @app.after_request
    def setup_csrftoken(response):
        """生成csrf_token"""
        csrf_token = generate_csrf()

        # 将csrf_token的值写入到cookie
        response.set_cookie('csrf_token', csrf_token)
        return response

    # 将自定义的过滤器函数添加到app过滤器列表中
    from info.utils.comment import do_ranK
    app.add_template_filter(do_ranK, 'rank')

    from info.utils.comment import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def page_not_found(e):
        """友好的404页面"""
        user = g.user
        context = {
            'user':user.to_dict() if user else None
        }
        return render_template('news/404.html',context=context)

    # 指定session数据存储在后端的位置
    Session(app)

    # 注册蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    # 注册蓝图
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    # 注册蓝图
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    # 注册蓝图
    from info.modules.user import user_blue
    app.register_blueprint(user_blue)

    return app