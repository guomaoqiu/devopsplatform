# -*- coding:utf-8 -*-
from . import salt
import time, json
from ..models import ApiMg
from flask import render_template,redirect,request,Response,flash,jsonify,url_for
from flask_login import login_required
from saltapi import SaltApi

@salt.route('/salttest')
@login_required
def salttest():
    '''
    @note: 运行salt命令
    '''

    api_info = ApiMg.query.filter_by(app_name='testfdsa').first()
    client = SaltApi('saltstack')
    cmd_params={'client': 'local', 'fun': 'cmd.run', 'tgt': '*', 'arg': 'date && hostname'}
    result_data = dict(dict(json.loads(client.saltCmd(cmd_params)))['return'][0]).values()[0]
    json_data=client.all_key()
    print "未认证的key: " , json_data['minions_denied']
    print "已认证key: " , json_data['minions']
    print "已拒绝key: " , json_data['minions_rejected']
    print "未认证key: " , json_data['minions_pre']

    host_info = client.get_minions('salt-api')
    print host_info
    #result_key = dict(dict(json.loads(client.all_key())))
    #print result_data
    return render_template('saltkey_list.html',data=json_data['minions'])
