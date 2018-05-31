# 主页模板
from . import index_blue
from flask import render_template,current_app,session,request,jsonify,g
from info.models import User,News,Category
from info import constants,response_code
from info.utils.comment import user_login_data

@index_blue.route('/new_list')
def index_news_list():
    """主页新闻列表数据
    1.接受参数（分页id,要看第几页，每页几条数据）
    2.校验参数（判断以上参数是否位数字）
    3.根据参数查询用户想看新闻数据
    4.构造相应的新闻列表数据
    5.响应新列表数据
    """
    # 1.接受参数
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')

    # 2校验参数
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    # 3.根据参数查询用户想看的新闻列表
    if cid == 1:
        # 从所有新闻中，根据时间倒序，每页取出10条数据
        paginate = News.query.order_by(News.create_time.desc()).paginate(page,per_page,False)
    else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page,per_page,False)

    # 4.构造相应的新闻的列表数据
    #     取出当前页的所有模型对象
    news_list = paginate.items
    # 读取分页总页数，将来在新闻主页列表上拉刷新时使用
    total_page = paginate.pages
    # 读取当前是第几页，将来在新闻主页列表上拉刷新时使用
    current_page = paginate.page

    # 将模型对象列表转成字典列表，让json在序列化时认识
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

        # 构造响应给客户端的数据
    data = {
        'news_dict_list': news_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }

    # 5.响应新闻列表数据
    return jsonify(errno=response_code.RET.OK, errmsg='ok', data=data)

@index_blue.route('/')
@user_login_data
def index():
    """主页
    1.处理网页右上角的用户显示数据，当用户已登陆‘展示用户名  退出  反之 展示登陆 注册
    2.新闻点击排行展示，在News 数据库表中查询，根据点击量clicks倒序
    3.新闻分类
    """
    # 1.处理网页右上角的用户显示数据
    # user_id = session.get('user_id',None)
    # user = None
    # if user_id:
    # # 1.表示用户登陆,查询用户信息
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 使用装饰器的g变量取出登录信息
    user = g.user

    # 2.新闻点击排行展示
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 3.新闻分类
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)

    # 构造渲染模板的上下文数据
    context = {
        'user':user,
        "news_clicks": news_clicks,
        'categories':categories

    }

    return render_template('news/index.html',context=context)

@index_blue.route('/favicon.ico',methods=['GET'])
def favicon():
    return current_app.send_static_file('news/favicon.ico')