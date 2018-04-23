# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: config.py
# @Date:   2018-02-28 11:57:30
# @Last Modified by:   guomaoqiu@sina.com
# @Last Modified time: 2018-04-19 17:18:09
import os
basedir = os.path.abspath(os.path.dirname(__file__))
from datetime import timedelta
from celery.schedules import crontab
class CeleryConfig(object):
    """后台任务配置"""
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_TASK_SERIALIZER = ['json','msgpack']
    
class Config:
    """基本配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A0Zr98j/3yXR~XHH!jmN]LWX/,?RT'
    #SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    BABEL_DEFAULT_LOCALE = 'zh'
    # 公司邮箱域名后缀，限制只能公司域名才能注册
    COMPANY_MAIL_SUFFIX='sctux.com'
    # 用户注册功能开关: True:可注册；False: 关闭注册
    REGISTER = False
    
    # send mail
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = u'[DevOpsPlatform]'
    FLASKY_MAIL_SENDER = '2399447849@qq.com'
    FLASKY_ADMIN = '2399447849@qq.com' # os.environ.get('FANXIANG_ADMIN')

    #加密解密所需的key
    PRPCRYPTO_KEY= '2d4g53sdfs6L6K'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = False
    db_host = '127.0.0.1'
    db_user = 'flask'
    db_pass = 'flask'
    db_name = 'flask4'
    SQLALCHEMY_DATABASE_URI = 'mysql://' + db_user + ':' + db_pass + '@' + db_host + '/' + db_name
    SQLALCHEMY_ECHO=False #用于显式地禁用或启用查询记录

    SQLALCHEMY_TRACK_MODIFICATIONS=True
    #RECAPTCHA_PUBLIC_KEY = '6LdCijkUAAAAAKo5KAdTE7XR7yA_PRvLHgmVlGeW'
    #RECAPTCHA_PRIVATE_KEY = '6LdCijkUAAAAAJTB0xosM4D_YTJmN3gxRmuJ-Jfj'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://flask:flask@127.0.0.1/flask-test'
    WTF_CSRF_ENABLED = False

class Production(Config):
    DEBUG = True
    db_host = '127.0.0.1'
    db_user = 'flask'
    db_pass = 'local_ops'
    db_name = 'local_ops'
    SQLALCHEMY_DATABASE_URI = 'mysql://' + db_user + ':' + db_pass + '@' + db_host + '/' + db_name
    SQLALCHEMY_ECHO=False #用于显式地禁用或启用查询记录

    ##SQLALCHEMY_DATABASE_URI = 'mysql://flask1:flask1@127.0.0.1/flask1'
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    #google 验证码
    #RECAPTCHA_PUBLIC_KEY = '6LdCijkUAAAAAKo5KAdTE7XR7yA_PRvLHgmVlGeW'
    #RECAPTCHA_PRIVATE_KEY = '6LdCijkUAAAAAJTB0xosM4D_YTJmN3gxRmuJ-Jfj'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': Production,
    'default': DevelopmentConfig
}
