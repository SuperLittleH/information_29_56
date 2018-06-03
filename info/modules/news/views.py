# 新闻详情和评论
from flask import  render_template,session,current_app,abort,g,jsonify,request
from . import news_blue
from info.models import User,News,Comment,CommentLike
from info import constants,db,response_code
from info.utils.comment import user_login_data


@news_blue.route('/comment_like',methods=['POST'])
@user_login_data
def comment_like():
    """新闻点赞和取消点赞"""
    # 1.获取登录用户的信息
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg="用户未登录")


    # 2.接受参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    # 3.校验参数
    if not all([comment_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")
    if action not in ['add','remove']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    # 4.根据客户端传入的comment_id查询出要点赞的评论
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="查询评论失败")
    if not comment:
        return jsonify(errno=response_code.RET.NODATA, errmsg="评论不存在")

    # 5.查询要点赞的评论的赞是否存在:查询等前用户是否给当前的评论点过赞
    try:
        comment_like_model = CommentLike.query.filter(CommentLike.comment_id==comment_id,CommentLike.user_id==user.id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="查询点赞失败")


    # 6.点赞和取消点赞
    if action == 'add':
        # 点赞
        if not comment_like_model:
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment_id
            # 将新的记录添加到数据库
            db.session.add(comment_like_model)
            # 累加点赞量
            comment.like_count += 1

    else:
        # 取消点赞
        if comment_like_model:
            # 将记录从数据库中删除
            db.session.delete(comment_like_model)
            # 减少点赞量
            comment.like_count -= 1


    # 7.同步到数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="操作失败")


    # 8.相应点赞和取消点赞的结果
    return jsonify(errno=response_code.RET.OK, errmsg="ok")

@news_blue.route('/news_comment',methods=["POST"])
@user_login_data
def news_comment():
    """新闻评论和回复评论"""
    # 1.获取登录用户的信息
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg="用户未登录")

    # 2.接受参数
    news_id = request.json.get('news_id')
    comment_content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    # 3.校验参数
    if not all([news_id,comment_content]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    # 4.查询要评论的新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="查询新闻数据失败")
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg="新闻数据不存在")

    # 5.实现新闻评论和回复评论逻辑
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_content

    # 回复评论
    if parent_id:
        comment.parent_id = parent_id

    # 同步数据到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="评论失败")

    # 6.响应评论结果
    return jsonify(errno=response_code.RET.OK, errmsg="ok",data=comment.to_dict())

@news_blue.route('/news_collect',methods=["GET",'POST'])
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
    6.展示用户的评论
    7.展示评论点的赞
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

    # 6.展示用户的评论
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    # 7.展示评论点的赞

    # 界面渲染数据时经过一个处理的
    comment_dict_list = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 给comment_dict追加一个is_like记录该评论是否被登录用户点赞了
        comment_dict['is_like'] = True
        # if
        #     comment_dict['is_like'] = True
        comment_dict_list.append(comment_dict)


    context = {
        'user':user,
        'news_clicks':news_clicks,
        'news':news.to_dict(),
        'is_collected':is_collected,
        'comments':comment_dict_list
    }

    # 渲染模板
    return render_template('news/detail.html',context=context)