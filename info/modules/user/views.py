# 个人中心
from . import user_blue
from flask import  render_template,g,redirect,url_for
from info.utils.comment import user_login_data

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
        'user':user
    }

    return render_template('news/user.html',context=context)