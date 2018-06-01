# 新闻详情
from flask import  render_template,session,current_app,abort,g
from . import news_blue
from info.models import User,News,db
from info import constants
from info.utils.comment import user_login_data


@news_blue.route('/news/collect')
@user_login_data
def news_collect():
    """新闻收藏"""
    pass

@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """新闻详情
    1.查询用户信息
    2.点击排行
    3.查询新闻详情
    4.累加点击量
    5.收藏和取消收藏
    """
    # 1.查询用户信息
    # 使用装饰器的g变量读取登录信息
    user = g.user

    # 2.点击排行
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 3.查询新闻详情
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    # 后续给404做个异常响应页面
    if not news:
        abort(404)

    # 4.累加点击量
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    # 5.收藏和取消收藏
    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True


    context = {
        'user':user,
        'news_clicks':news_clicks,
        'news':news.to_dict(),
        'is_collected':is_collected
    }

    # 渲染模板
    return render_template('news/detail.html',context=context)