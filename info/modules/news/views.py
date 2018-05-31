# 新闻详情
from flask import  render_template,session,current_app,abort
from . import news_blue
from info.models import User,News
from info import constants

@news_blue.route('/detail/<int:news_id>')
def news_detail(news_id):
    """新闻详情
    1.查询用户信息
    2.点击排行
    3.查询新闻详情
    """
    # 1.查询用户信息
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        # 1.表示用户登陆,查询用户信息
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

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
    context = {
        'user':user,
        'news_clicks':news_clicks,
        'news':news.to_dict()
    }

    # 渲染模板
    return render_template('news/detail.html',context=context)