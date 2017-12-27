from flask_script import Manager, Shell
from app import create_app, db, celery
from app.models import User, Role, Permission,LoginLog
import os
from flask_migrate import Migrate, MigrateCommand, upgrade

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

#db = SQLAlchemy(app)

manager = Manager(app,db)
migrate = Migrate(app,db)

def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, LoginLog=LoginLog)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
