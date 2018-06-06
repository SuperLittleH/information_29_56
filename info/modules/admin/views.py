# 后台管理
from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for,g
from info.models import User
from info.utils.comment import user_login_data


@admin_blue.route('/user_count)')
def user_count():
    """用户量统计"""
    # 1.用户总数
    total_count = 0

    # 2.月新增数
    month_count = 0


    # 3.日新增数
    day_count = 0

    context = {
        'total_count':total_count,
        'month_count':month_count,
        'day_count':day_count
    }

    return render_template('admin/user_count.html',context=context)

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