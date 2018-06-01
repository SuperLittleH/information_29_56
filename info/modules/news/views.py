# 新闻详情
from flask import  render_template,session,current_app,abort,g,jsonify,request
from . import news_blue
from info.models import User,News
from info import constants,db,response_code
from info.utils.comment import user_login_data


@news_blue.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    """新闻收藏"""
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR,errmsg='用户未登录')

    # 2.接受参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 3.校验参数
    if not all([news_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='缺少参数')
    if action not in ['collect','cancel_collect']:
        return jsonify(errno=response_code.RET.PARAMERR,errmsg='参数错误')

    # 4.查询新闻信息
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR,errmsg='查询新闻数据失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA,errmsg='新闻数据不存在')

    # 5.收藏和取消收藏新闻
    if action == 'collect':
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
            user.collection_news.remove(news)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR,errmsg='收藏操作失败')

    # 6.响应操作结果
    return jsonify(errno=response_code.RET.OK,errmsg='操作成功')

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