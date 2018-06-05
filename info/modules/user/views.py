# 个人中心
from . import user_blue
from flask import  render_template,g,redirect,url_for,request,jsonify,current_app,session
from info.utils.comment import user_login_data
from info import response_code,db,constants
from info.utils.file_storage import upload_file
from info.models import Category,News


@user_blue.route('/news_list')
@user_login_data
def user_news_list():
    """我发布的新闻列表"""
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.接受参数
    page = request.args.get('p','1')

    # 3.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 4.分页查询
    news_list = []
    current_page = 1
    total_page = 1
    try:
        paginate = News.query.filter(News.user_id==user.id).paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
        # 5.构造渲染模板的数据
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    context = {
        'news_list':news_dict_list,
        'current_page':current_page,
        'total_page':total_page
    }

    # 6.渲染界面
    return render_template('news/user_news_list.html',context=context)

@user_blue.route('/news_release',methods=["GET","POST"])
@user_login_data
def user_news_release():
    """新闻发布"""
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.get请求的逻辑:渲染发布新闻的界面
    if request.method == 'GET':
        # 2.1渲染新闻分类数据
        categories = []
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        # 删除最新类
        categories.pop(0)

        context = {
            'categories':categories
        }

        return render_template('news/user_news_release.html',context=context)

    # 3.POST请求逻辑:实现新闻发布的逻辑
    if request.method == 'POST':
        # 3.1接收参数
        title = request.form.get("title")
        source = "个人发布"
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")

        # 3.2校验参数
        if not all([title, source, digest, content, index_image, category_id]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")

        # 3.3读取用户上传的新闻的图片
        try:
            index_image_data = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="读取新闻图片失败")

        # 3.4将用户上传的新闻图片转存至七牛
        try:
            key = upload_file(index_image_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg="上传新闻图片失败")

        # 3.5创建NEWS模型对象,并同步到数据库
        news = News()
        news.title = title
        news.digest = digest
        news.source = source
        news.content = content
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        news.category_id = category_id
        news.user_id = g.user.id
        # 1代表待审核状态
        news.status = 1

        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="保存新闻数据失败")

        # 3.6响应新闻发布的结果
        return jsonify(errno=response_code.RET.OK, errmsg="发布新闻成功")
@user_blue.route('/user_collection')
@user_login_data
def user_collection():
    """用户收藏"""

    # 1.获取用户登陆信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.接受参数
    page = request.args.get('p','1')

    # 3.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page ='1'

    # 4.分页查询
    paginate = None
    try:
        paginate = user.collection_news.paginate(page,constants.USER_COLLECTION_MAX_NEWS,False)
    except Exception as e:
        current_app.logger.error(e)

    # 5.构造渲染模板的数据
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())

    context = {
        'news_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }
    # 渲染模板
    return render_template('news/user_collection.html',context=context)

@user_blue.route('/pass_info',methods=['GET','POST'])
@user_login_data
def pass_info():
    """修改密码"""

    # 1.获取参数用户信息
    user = g.user
    if not user:
        return render_template(url_for('index.index'))

    # 2.实现get请求的逻辑
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')

    # 3.pass请求逻辑
    if request.method == "POST":
        # 3.1接收参数
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')

        # 3.2校验参数
        if not all([old_password,new_password]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")

        # 判断输入的旧密码是否是该登陆用户的密码
        if not user.check_passowrd(old_password):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="原密码输入有误")

        # 3.3更新密码
        user.password = new_password

        # 3.4同步到数据库
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.OK, errmsg="保存密码失败")

        # 3.5响应修改密码的结果
        return jsonify(errno=response_code.RET.OK, errmsg="修改密码成功")

@user_blue.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    """设置头像"""

    # 1.获取登陆信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.实现get请求逻辑
    if request.method == "GET":
        # 构造渲染数据的上下文
        context = {
            'user':user.to_dict()
        }

        # 渲染界面
        return render_template('news/user_pic_info.html',context=context)

    # 3.post请求逻辑:上传图片
    if request.method == "POST":
        # 3.1获取参数
        avatar_file = request.files.get('avatar')

        # 3.2校验参数
        try:
            avatar_data = avatar_file.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="读取头像数据失败")

        # 3.3调用上传的方法,将图片上传至七牛
        try:
            key = upload_file(avatar_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.THIRDERR, errmsg="上传失败")

        # 3.4保存用户头像的key到数据库
        user.avatar_url = key
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="保存用户头像失败")

        data = {
            'avatar_url': constants.QINIU_DOMIN_PREFIX + key
        }

        # 3.5响应头像的上传的结果
        return jsonify(errno=response_code.RET.OK, errmsg="上传成功", data=data)


@user_blue.route('/base_info',methods=['GET','POST'])
@user_login_data
def base_info():
    """基本资料"""

    #1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.实现GET请求的逻辑
    if request.method == "GET":
        # 构造渲染数据的上下文
        context = {
            'user':user.to_dict()
        }
        # 渲染界面
        return render_template('news/user_base_info.html',context=context)

    # 3.POST请求逻辑
    if request.method == "POST":
        # 3.1获取参数
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')

        # 3.2校验参数
        if not all([nick_name,signature,gender]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")
        if gender not in ['MAN','WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg="参数错误")

        # 3.3修改用户的基本资料
        user.signature = signature
        user.nick_name = nick_name
        user.gender = gender

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR, errmsg="修改用户资料失败")

        # 4.注意:修改了昵称以后记得将状态保持中的昵称也修改
        session['nick_name'] = nick_name

        # 5.响应修改结果
        return jsonify(errno=response_code.RET.OK, errmsg="修改基本资料成功")

@user_blue.route('/info')
@user_login_data
def user_info():
    """个人中心入口"""
    # 提示:必须是登录用户才能进入

    # 获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    context = {
        'user':user.to_dict()
    }

    return render_template('news/user.html',context=context)