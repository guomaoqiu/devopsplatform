# -*- coding: utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from config import CeleryConfig
from celery import Celery
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

celery = Celery(app.name, broker=CeleryConfig.CELERY_BROKER_URL,backend=CeleryConfig.CELERY_RESULT_BACKEND)

csrf = CSRFProtect()
db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    csrf.init_app(app)

    # update celery  config
    celery.conf.update(app.config)
    db.init_app(app)
    db.app = app
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)


    login_manager.init_app(app)
    # create tables
    with app.test_request_context():
        db.create_all()

    from auth import auth as auth_blueprint
    from main import main as main_blueprint
    from salt import salt as salt_blueprint
    from task import task as task_blueprint
    from zabbix import zabbix as zabbix_blueprint
    from data import data as data_blueprint

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(main_blueprint)
    app.register_blueprint(salt_blueprint)
    app.register_blueprint(task_blueprint)
    app.register_blueprint(zabbix_blueprint)
    app.register_blueprint(data_blueprint)

    return app
