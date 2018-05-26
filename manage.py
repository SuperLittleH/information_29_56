from flask_script import Manager
from flask_migrate import MigrateCommand,Migrate
# from info import app,db
from info import create_app,db

# 创建app
app = create_app('dev')
# 创建脚本管理器对象
manager = Manager(app)

# 让迁移和app和数据库建立关联
Migrate(app,db)

# 将数据库迁移到一个脚本添加到manager
manager.add_command('mysql',MigrateCommand)

if __name__ == '__main__':
    manager.run()