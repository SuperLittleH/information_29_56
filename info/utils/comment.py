# 公共的工具类文件
from flask import session,current_app,g
from info.models import User
from functools import wraps

def do_ranK(index):
    """根据index返回对应的first,second,third"""
    if index == 1:
        return 'first'
    elif index ==2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''


def user_login_data(view_func):
    # 使用装饰器获取登录信息

    # 提示：wraps函数会拦截到传给装饰器函数的参数
    # 装饰器会修改被拦截的函数的__name__属性，会将所有的被装饰的函数都叫wrapper
    # 解决：@wraps(view_func):会将被装饰的函数的___name__属性还原
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id', None)
        user = None
        if user_id:
            # 1.表示用户登陆,查询用户信息
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        # 使用全局g变量存取查询登录用户信息
        g.user = user

        # 执行被装饰的试图函数
        return view_func(*args,**kwargs)

    return wrapper