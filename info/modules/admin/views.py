# 后台管理
from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for,g,abort
from info.models import User,News
from info.utils.comment import user_login_data
import time,datetime
from info import constants

@admin_blue.route('/news_review')
def news_review():
    """后台新闻审核列表"""

    # 1.接受参数
    page = request.args.get('p','1')

    # 2.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 3.分页查询
    news_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = News.query.filter(News.status != 0).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        news_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    # 4.构造渲染数据
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    context = {
        'news_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }
    # 5.响应结果
    return render_template('admin/news_review.html',context=context)


@admin_blue.route('/user_list')
def user_list():
    """用户列表"""
    # 接受参数
    page = request.args.get('p','1')

    # 校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 查询用户列表管理员除外
    users = []
    total_page = 1
    current_page = 1
    try:
        paginate = User.query.filter(User.is_admin==False).paginate(page,constants.ADMIN_USER_PAGE_MAX_COUNT,False)
        users = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    user_dict_list = []
    for user in users:
        user_dict_list.append(user.to_admin_dict())

    # 构造渲染数据
    context = {
        'users':user_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }

    return render_template('admin/user_list.html',context=context)

@admin_blue.route('/user_count)')
def user_count():
    """用户量统计"""

    # 1.用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)


    # 2.月新增数
    month_count = 0
    # 计算每月的开始时间
    t = time.localtime()
    # 计算每月开始时间字符串
    month_begin = '%d-%02d-01' % (t.tm_year,t.tm_mon)
    # 计算每月开时间对象
    month_begin_date = datetime.datetime.strptime(month_begin,'%Y-%m-%d')
    try:
        month_count = User.query.filter(User.is_admin==False,User.create_time>month_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
    # 3.日新增数
    day_count = 0
    # 计算当天开始时间
    t = time.localtime()
    day_begin = '%d-%02d-%02d' % (t.tm_year,t.tm_mon,t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin,'%Y-%m-%d')
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 每日用户登陆用户活跃量
    # 存放时间节点
    active_date = []
    # 存放活跃量
    active_count = []

    # 查询今天开始的时间
    # 获取当天开始时间字符串
    today_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    # 获取开始时间对象
    today_begin_date = datetime.datetime.strptime(today_begin, '%Y-%m-%d')

    for i in range(0, 15):
        # 计算一天开始
        begin_date = today_begin_date - datetime.timedelta(days=i)
        # 计算一天结束
        end_date = today_begin_date - datetime.timedelta(days=(i - 1))

        # 将x轴对应的开始时间记录
        active_date.append(datetime.datetime.strftime(begin_date, '%Y-%m-%d'))

        #     查询当天的用户的用户量
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
            active_count.append(count)
        except Exception as e:
            current_app.logger.error(e)

    # 反转列表保证时间从左至右时递增
    active_date.reverse()
    active_count.reverse()

    context = {
        'total_count': total_count,
        'month_count': month_count,
        'day_count': day_count,
        'active_date': active_date,
        'active_count': active_count

    }

    return render_template('admin/user_count.html', context=context)

@admin_blue.route('/')
@user_login_data
def admin_index():
    """主页"""
    # 获取登陆用户信息
    user = g.user
    if not user:
        return redirect(url_for('admin.admin_login'))
    # 构造渲染数据
    context = {
        'user': user.to_dict()
    }
    # 渲染模板
    return render_template('admin/index.html', context=context)



@admin_blue.route('/login',methods=['GET','POST'])
def admin_login():
    """登陆"""
    # get提供登陆界面
    if request.method == "GET":
        # 获取用户登陆信息,如果用户登陆直接进入主页
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))

        return render_template('admin/login.html')

    # POST
    if request.method == "POST":
        # 1.获取参数
        username = request.form.get('username')
        password = request.form.get('password')

        # 2.校验参数
        if not all([username,password]):
            return render_template('admin/login.html',errmsg='缺少参数')


        # 3.查询当前要登陆的用户是否存在
        try:
            user = User.query.filter(User.nick_name==username).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/login.html', errmsg='查询用户数据失败')
        if not user:
           return render_template('admin/login.html', errmsg='用户名或者密码错误')

        # 4.对比当前登陆的用户的密码
        if not user.check_passowrd(password):
            return render_template('admin/login.html', errmsg='用户名或者密码错误')

        # 5.将状态保持写入session
        session['user_id'] = user.id
        session['nick_name'] = user.nick_name
        session['mobile'] = user.mobile
        session['is_admin'] = user.is_admin

        # 6.响应登陆结果
        return redirect(url_for('admin.admin_index'))