# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, PasswordField

from wtforms.validators import DataRequired, Length, Email , EqualTo, Regexp, Required
from wtforms import ValidationError
from ..models import User,Role
from .. import db

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ApiForm(FlaskForm):
    app_name = StringField('应用名称', validators=[Required(),Length(0, 64)])
    api_user = StringField('Api用户', validators=[Required(),Length(0, 64)])
    api_paas = StringField('API密码', validators=[Required(),Length(0, 64)])
    api_url = StringField('API地址', validators=[Required(),Length(0, 64)])
    submit = SubmitField('Submit')

class DataForm(FlaskForm):
    data_content = TextAreaField('表名称:')
    client_version = StringField('客户端版本号(务必保证正确填写)', validators=[Length(0, 64)])
    submit = SubmitField('提交') 

class ResDataForm(FlaskForm):
    res_version = StringField('热更版本号', validators=[Length(0, 64)])
    client_version = StringField('客户端版本号(务必保证正确填写)', validators=[Length(0, 64)])
    submit = SubmitField('提交')     

# online
class DataFormOnline(FlaskForm):
    data_content = TextAreaField('表名称:')
    submit = SubmitField('提交')

class ResDataFormOnline(FlaskForm):
    res_version = StringField('热更版本号', validators=[Length(0, 64)])
    submit = SubmitField('提交') 

class AccessForm(FlaskForm):
    ip = StringField('IP地址', validators=[Required(),Length(0, 64)])
    remark = StringField('备注', validators=[Required(),Length(0, 64)])
    submit = SubmitField('提交') 

class UidForm(FlaskForm):
    uid_content = TextAreaField('UID(多个UID请以英文逗号分隔)')
    submit = SubmitField('提交') 

class WebsshForm(FlaskForm):
    host = StringField('主机', validators=[Length(0, 64)])
    port = StringField('端口', validators=[Length(0, 64)])
    username = StringField('用户名', validators=[Length(0, 64)])
    password = StringField('密码', validators=[Length(0, 64)])
    # submit = SubmitField('连接')

class EditorUidForm(FlaskForm):
    do_action = StringField('Action')
    file_data = TextAreaField('File Data')

class EditorForm(FlaskForm):
    do_action = StringField('Action')
    file_path = StringField('File Path', validators=[DataRequired()])
    file_data = TextAreaField('File Data')
