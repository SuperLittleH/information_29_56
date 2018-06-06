from flask import Blueprint,session,redirect,url_for,request

# 创建蓝图对象
admin_blue = Blueprint('admin',__name__,url_prefix='/admin')

from . import views

@admin_blue.before_request
def check_admin():
    """验证用户的身份"""
    is_admin = session.get('is_admin',False)

    # 1.判断是否是管理员:只有管理员才能进入管理后台
    # 2.当无论哪种用户访问后台的登陆界面都是可以访问
    # 2.1前台可以登陆但是登陆不上后台主页
    # 2.2如果是后台用户可以登陆
    # 3.如果管理员登陆了后台管理又进入前台会留下session
    if not is_admin and not request.url.endswith('/admin/login') :
        return redirect(url_for('index.index'))