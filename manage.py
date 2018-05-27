from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate
# from info import app,db
from info import create_app,db,models

# 创建app
app = create_app('dev')
# 创建脚本管理器对象
manager = Manager(app)

# 让迁移和app和数据库建立关联
Migrate(app,db)

# 将数据库迁移到一个脚本添加到manager
manager.add_command('mysql',MigrateCommand)

# @app.route('/')
# def index():
#     # 测试redis数据库
#     # redis_store.smanage.py:55et('name','itheima')
#
#     # 测试session
#     # from flask import session
#     # 会将('age':'2')写入cookie
#     # session['age'] = '2'
#
#     return 'index'

if __name__ == '__main__':
    manager.run()