# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: manager.py
# @Date:   2018-03-13 17:42:01
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-03-13 17:46:07

# from gevent import monkey
# from gevent.pywsgi import WSGIServer
# from geventwebsocket.handler import WebSocketHandler

from flask_script import Manager, Shell
from app import create_app, db, celery
from app.models import User, Role, Permission,LoginLog
import os
from flask_migrate import Migrate, MigrateCommand, upgrade
from livereload import Server

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app,db)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, LoginLog=LoginLog)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def dev():
  # 遍历所有文件进行watch,便于实施加载，开发
  live_server = Server(app.wsgi_app)
  # os.getcdw()获取当前文件所在目录位置
  for root, dirs, files in os.walk(os.getcwd()): 
      for name in files:
          filepath=os.path.join(root, name)
          live_server.watch(filepath,ignore=False)
  live_server.serve(open_url=False)

if __name__ == '__main__':
    manager.run()
