# 后台管理
from . import admin_blue
from flask import render_template,request,current_app,session,redirect,url_for
from info.models import User


@admin_blue.route('/')
def admin_index():
    """主页"""
    return render_template('admin/index.html')


@admin_blue.route('/login',methods=['GET','POST'])
def admin_login():
    """登陆"""
    # get提供登陆界面
    if request.method == "GET":
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