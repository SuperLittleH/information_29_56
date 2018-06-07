# 后台管理
from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for,g,abort,jsonify
from info.models import User,News,Category
from info.utils.comment import user_login_data
import time,datetime
from info import constants,response_code,db
from info.utils.file_storage import upload_file

@admin_blue.route('/news_edit_detail/<int:news_id>',methods=['GET','POST'])
def news_edit_detail(news_id):
    """新闻版式编辑详情"""
    if request.method == 'GET':
        #查询要编辑的新闻
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)
        if not news:
            abort(404)

        # 查询分类
        categories = []
        try:
            categories = Category.query.all()
            categories.pop(0)
        except Exception as e:
            current_app.logger.error(e)
            abort(404)

        # 构造渲染数据
        context = {
             'news':news.to_dict(),
             'categories':categories
         }

        return render_template('admin/news_edit_detail.html',context=context)

    if request.method == "POST":
        # 1.接受参数
        title = request.form.get('title')
        digest = request.form.get('digest')
        content = request.form.get('content')
        index_image = request.form.get('index_image')
        category_id = request.form.get('category_id')
        # status = request.form.get('status')

        # 2.校验参数
        if not all([news_id,title,digest,content,category_id]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")

        # 3.查询要编辑的新闻
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="查询新闻数据失败")

        if not news:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="新闻不存在")

        # 4.读取和上传图片
        if index_image:
            try:
                index_image = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.PARAMERR, errmsg="读取新闻图片失败")

            # 5.将图片上传到七牛
            try:
                key = upload_file(index_image)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.THIRDERR, errmsg="上传失败")

            news.index_image_url = constants.QINIU_DOMIN_PREFIX + key

        # 6.保存数据并同步到数据库
        news.title = title
        news.digest =digest
        news.content = content
        news.category_id = category_id
        # news.status = 1


        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="保存数据失败")

        # 7.响应结果
        return jsonify(errno=response_code.RET.OK, errmsg="OK")


@admin_blue.route('/news_edit')
def news_edit():
    """新闻版式编辑列表"""
    # 1.接受参数
    page = request.args.get('p','1')
    keyword = request.args.get('keyword')

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
        if keyword:
            paginate = News.query.filter(News.title.contains(keyword),News.status == 0).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        else:
            paginate = News.query.filter(News.status==0).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
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

    return render_template('admin/news_edit.html',context=context)


@admin_blue.route('/news_review_action',methods=['POST'])
def news_review_action():
    """审核新闻的实现"""

    # 1.接受参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 2.校验参数
    if not all([news_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")
    if not action in ['accept','reject']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

    # 3.查询新闻是否存在
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="查询新闻失败")
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg="新闻不存在")

    # 4.实现审核逻辑
    if action == 'accept':
        # 通过
        news.status = 0
    else:
        # 拒绝通过
        news.status =-1
        # 拒绝原因
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少拒绝理由")
        news.reason = reason

    # 5.同步到数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=response_code.RET.OK, errmsg="OK")


@admin_blue.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    """待审核新闻详情"""

    # 1.查询出要审核的新闻的详情
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    if not news:
        abort(404)

    # 2.构造渲染数据
    context = {
        'news':news.to_dict()
    }


    return render_template('admin/news_review_detail.html',context=context)

@admin_blue.route('/news_review')
def news_review():
    """后台新闻审核列表"""

    # 1.接受参数
    page = request.args.get('p','1')
    keyword = request.args.get('keyword')

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
        if keyword:
            paginate = News.query.filter(News.title.contains(keyword),News.status != 0).order_by(News.create_time.desc()).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
        else:
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