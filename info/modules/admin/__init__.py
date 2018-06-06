from flask import Blueprint,session,redirect,url_for

# 创建蓝图对象
admin_blue = Blueprint('admin',__name__,url_prefix='/admin')

from . import views

@admin_blue.before_request
def check_admin():
    """验证用户的身份"""
    is_admin = session.get('is_admin',False)


    # 1.判断是否是管理员
    if not is_admin:
        return redirect(url_for('index.index'))