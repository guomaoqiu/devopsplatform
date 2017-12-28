# -*- coding:utf-8 -*-
from . import salt
import time, json
from ..models import ApiMg
from flask import render_template,redirect,request,Response,flash,jsonify,url_for
from flask_login import login_required
from saltapi import SaltApi
from .. import db


@salt.route('/apitest',methods=['GET','POST'])
#@login_required
def apitest():
    if request.method == 'POST':
        client = SaltApi(app_name='saltstack')
        if client.login_test(app_name='saltstack'):
             return  jsonify({"result":True,"message":"SaltApi连接正常"})
        else:
             return  jsonify({"result":False,"message":"SaltApi连接异常"})
    

@salt.route('/saltkeylist')
@login_required
def saltkeylist():
    '''
    @note: 运行salt命令
    '''
    client = SaltApi(app_name='saltstack')

    #api_info = ApiMg.query.filter_by(app_name='saltstack').first()
 
    json_data=client.all_key()
   
    print "未认证的key: " , json_data['minions_denied']
    print "已认证key: " , json_data['minions']
    print "已拒绝key: " , json_data['minions_rejected']
    print "未认证key: " , json_data['minions_pre']
   
    return render_template('saltstack/saltkey_list.html',data=json_data['minions'])

# saltstack minion connection test
@salt.route('/salt_minion_test',methods=['GET','POST'])
@login_required
def salt_minion_test():
 
    if request.method == 'POST':
        key_name = json.loads(request.form.get('data'))['key_name']
        client = SaltApi(app_name='saltstack')
        testping = json.loads(client.saltCmd(params={'client': 'local', 'fun': 'test.ping', 'tgt': key_name}))['return'][0].values()
        if testping[0]:
            return  jsonify({"result":True,"message":" Minion【%s】连接正常" % key_name })
    return  jsonify({"result":False,"message":"Minion连接异常"})
