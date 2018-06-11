# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: models.py
# @Date:   2018-03-30 14:44:19
# @Last Modified by:   guomaoqiu@sina.com
# @Last Modified time: 2018-06-05 15:44:56

from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        '''
        # 创建数据库时需要指定编码为UTF8;
        CREATE DATABASE `flask4` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
        grant all on flask4.* to flask@'%' identified by 'flask';
        flush privileges;
        #
        #python manage.py shell
        from manager import Role
        Role.insert_roles()
        Role.query.all()
        [<Role u'Moderator'>, <Role u'Administrator'>, <Role u'User'>]
        '''
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff , False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    avatar_hash = db.Column(db.String(32))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property 
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        # 添加密码时对密码加密
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        # 确认功能
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        # 获取token
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        # 重置密码
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        # 更改邮箱时获得token
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        # 更改邮箱
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        # 判断用户是否是管理员
        return self.can(Permission.ADMINISTER)

    def ping(self):
        # 记录登录时间
        self.last_seen = datetime.now()
        db.session.add(self)


    def gravatar(self, size=100, default='identicon', rating='g'):
        # 用户头像
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    def __repr__(self):
        return '<User %r>' % self.username

    def to_json(self):
        return {
                'id': self.id,
                'email': self.email,
                'username': self.username,
                'role_id': self.role_id,
                'confirmed': self.confirmed, 
                'name': self.name,
                'member_since': self.member_since,

                }

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginLog(db.Model):
    __tablename__ = 'login_log'
    id = db.Column(db.Integer, primary_key=True)
    loginuser = db.Column(db.String(64))
    logintime = db.Column(db.String(64))
    login_browser = db.Column(db.String(200))
    login_ip = db.Column(db.String(64))

    def to_json(self):
        return {
                'id': self.id,
                'loginuser': self.loginuser,
                'logintime': self.logintime,
                'login_browser':self.login_browser,
                'login_ip': self.login_ip,
                }


# api 管理
class ApiMg(db.Model):
    __tablename__ = 'api_manager'
    id = db.Column(db.Integer, primary_key=True)
    app_name =  db.Column(db.String(64), unique=True, index=True)
    api_user = db.Column(db.String(64), unique=True, index=True)
    api_paas = db.Column(db.String(64), unique=True, index=True)
    api_token = db.Column(db.String(64), unique=True, index=True)
    create_time = db.Column(db.DateTime(), default=datetime.now)
    api_url = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '%s' % self.app_name

    def api_create_time(self):
        return self.create_time

    def api_token_res(self):
        return self.api_token

    def to_json(self):
        return {
            "id": self.id,
            "app_name":self.app_name,
            "api_user":self.api_user,
            "api_token": self.api_token,
            "create_time":self.create_time,
            "api_paas": self.api_paas,
            "api_url": self.api_url
        }

# 平台访问白名单:
class AccessIpList(db.Model):
    __tablename__ = 'access_ip_list';
    id = db.Column(db.Integer, primary_key=True)
    create_user = db.Column(db.String(64))
    create_time = db.Column(db.DateTime(), default=datetime.now)
    remark = db.Column(db.String(64))
    ip = db.Column(db.String(64))

    def to_json(self):
        return {
            "id": self.id,
            "create_user":self.create_user,
            "create_time":self.create_time,
            "remark": self.remark,
            "ip":self.ip,

        }

# 主机信息
class Hostinfo(db.Model):
    __tablename__ = 'server_info_list'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64))
    external_ip = db.Column(db.String(64))
    private_ip = db.Column(db.String(64))
    mem_total = db.Column(db.String(64))
    cpu_type = db.Column(db.Text())
    num_cpus = db.Column(db.String(64))
    os_release = db.Column(db.String(64))
    kernelrelease = db.Column(db.Text())

    def to_json(self):
        return {
                'id':self.id,
                'hostname' : self.hostname,
                'external_ip' : self.external_ip,
                'private_ip' : self.private_ip,
                'mem_total' : self.mem_total,
                'cpu_type'  : self.cpu_type,
                'num_cpus' : self.num_cpus,
                'os_release': self.os_release,
                'kernelrelease': self.kernelrelease
        }
        
class DataApi(db.Model):

    __tablename__ = 'dataapi'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(64), unique=False)
    create_time = db.Column(db.DateTime(), default=datetime.now)

    def to_json(self):
        return {
            "name": self.data,
            "create_time": self.create_time
        }


# 命令执行记录
# runcmd log
class RuncmdLog(db.Model):
    __tablename__ = 'runcmdlog'
    id = db.Column(db.Integer, primary_key=True)
    runcmd_target =  db.Column(db.String(64))
    runcmd_cmd = db.Column(db.String(64))
    runcmd_time = db.Column(db.DateTime(), default=datetime.now)
    runcmd_user =db.Column(db.String(64))
    runcmd_result = db.Column(db.Text())

    def to_json(self):
        return {
            "id": self.id,
            "runcmd_target": self.runcmd_target,
            "runcmd_cmd":self.runcmd_cmd,
            "runcmd_time":self.runcmd_time,
            "runcmd_user": self.runcmd_user,
            "runcmd_result": self.runcmd_result
        }

