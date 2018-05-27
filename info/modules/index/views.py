from . import index_blu
@index_blu.route('/index')
def index():
    # 测试redis数据库
    # redis_store.set('name','itheima')

    # 测试session
    # from flask import session
    # 会将('age':'2')写入cookie
    # session['age'] = '2'
    return "index"