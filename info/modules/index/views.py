# 主页模板
from . import index_blue
from flask import render_template,current_app,session
from info.models import User,News
from info import constants

@index_blue.route('/')
def index():
    """主页
    1.处理网页右上角的用户显示数据，当用户已登陆‘展示用户名  退出  反之 展示登陆 注册
    2.新闻点击排行展示，在News 数据库表中查询，根据点击量clicks倒序
    """
    # 1.处理网页右上角的用户显示数据
    user_id = session.get('user_id',None)
    user = None
    if user_id:
    # 1.表示用户登陆,查询用户信息
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 2.新闻点击排行展示
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)


    # 构造渲染模板的上下文数据
    context = {
        'user':user,
        "news_clicks": news_clicks

    }

    return render_template('news/index.html',context=context)

@index_blue.route('/favicon.ico',methods=['GET'])
def favicon():
    return current_app.send_static_file('news/favicon.ico')