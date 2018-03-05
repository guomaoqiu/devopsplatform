# -*- coding:utf-8 -*-
from . import salt
import time, json
from ..models import ApiMg,Hostinfo
from flask import render_template,redirect,request,Response,flash,jsonify,url_for
from flask_login import login_required
from saltapi import SaltApi
from .. import db

@salt.route('/saltkeylist',methods=['GET','POST'])
@login_required
def saltkeylist():
    '''
    @note: 运行salt命令
    '''
    if request.method == "POST":
        if not ApiMg.query.filter_by(app_name='saltstackapi').first():
            return jsonify({"result": False, "message": u'请确保API信息已录入！'})
    try:
        client = SaltApi()
        data=client.all_key()
        print "未认证的key: " , data['minions_denied']
        print "已认证key: " , data['minions']
        print "已拒绝key: " , data['minions_rejected']
        print "未认证key: " , data['minions_pre']
        print data
        return render_template('saltstack/saltkey_list.html',data=data['minions'])
    except Exception,e:
        print e
        flash("未能正常连接saltapi,请检查api配置",'danger')
        return render_template('saltstack/saltkey_list.html',data='')


# saltstack minion connection test
@salt.route('/salt_minion_test',methods=['GET','POST'])
@login_required
def salt_minion_test():

    if request.method == 'POST':
        key_name = json.loads(request.form.get('data'))['key_name']
        client = SaltApi()
        testping = json.loads(client.saltCmd(params={'client': 'local', 'fun': 'test.ping', 'tgt': key_name}))['return'][0].values()
        if testping[0]:
            return  jsonify({"result":True,"message":" Minion【%s】连接正常" % key_name })
    return  jsonify({"result":False,"message":"Minion连接异常"})

@salt.route('/deploy',methods=['GET','POST'])
@login_required
def deploy():
    host_list = Hostinfo.query.all()
    data = []
    [ data.append(i.to_json()) for i in host_list ]

    return  render_template('saltstack/soft_deploy.html',data=data)



@salt.route('/file_push',methods=['GET','POST'])
@login_required
def file_push():
    '''
    @note: 文件分发
    '''
    #client = SaltApi()
    #testping = client.saltCmd(params={'client': 'local', 'fun': 'cp.get_file', 'tgt': '*' ,'arg':'salt://file1 /tmp/file1'})
    #print testping
    return render_template('saltstack/file_push.html')
        


@salt.route('/saltcmd/<hostname>',methods=['GET','POST'])
@login_required
def saltcmd(hostname):
    '''
    @note: 文件分发
    '''
    print hostname
    if request.method == "POST":
        print request.method
    return render_template('saltstack/saltcmd.html',hostname=hostname)

@salt.route('/run_saltcmd',methods=['GET','POST'])
@login_required
def run_saltcmd():
    '''
    @note: 文件分发
    '''
    
    if request.method == "POST":
        print request.method
    return render_template('saltstack/saltcmd.html',)              