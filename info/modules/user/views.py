# 个人中心
from . import user_blue
from flask import  render_template

@user_blue.route('/info')
def user_info():
    """个人中心入口"""
    return render_template('news/user.html')