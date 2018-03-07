# -*- coding:utf-8 -*-
from . import salt
import time, json
from flask_login import current_user
from ..models import ApiMg,Hostinfo,RuncmdLog
from flask import render_template,redirect,request,Response,flash,jsonify,url_for
from flask_login import login_required
from saltapi import SaltApi
from .. import db
import os

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
    @note: 命令执行页面
    '''
    if ApiMg.query.filter_by(app_name='saltstackapi').first():
        return render_template('saltstack/saltcmd.html',has_api=True,hostname=hostname)
    else:
        return render_template('saltstack/saltcmd.html',has_api=False,hostname=hostname)     

@salt.route('/run_saltcmd',methods=['GET','POST'])
@login_required
def run_saltcmd():
    '''
    @note: 命令执行
    '''
    if request.method == "POST":
        cmd=json.loads(request.form.get('data'))['cmd']
        hostname=json.loads(request.form.get('data'))['hostname']
        
        # 读取命令黑名单
        with open(os.path.split(os.path.realpath(__file__))[0] + "/" + "block_cmd.txt", 'r') as f:
            for each_cmd in f.readlines():
                print each_cmd.strip('\n')
                if cmd in each_cmd:
                    return jsonify({"result": False,"message": u'禁止在此平台运行该命令'})
                client = SaltApi()        
                print cmd,hostname
                run_cmd = json.loads(client.saltCmd(params={'client': 'local', 'fun': 'cmd.run', 'tgt': '%s' % hostname, 'arg': '%s' % cmd}))['return'][0].values()
                t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                run_cmd_log = RuncmdLog(runcmd_target=hostname,runcmd_cmd=cmd, runcmd_user=current_user.name,runcmd_result=run_cmd)
                db.session.add(run_cmd_log)
                db.session.commit()
                return jsonify({"result": True,"data": run_cmd,"run_time": t,"message": u'执行成功'})
    return render_template('saltstack/saltcmd.html')


@salt.route('/run_salt_cmd', methods=['GET', 'POST'])
@login_required
def run_salt_cmd():
    host_list = Hostinfo.query.all()
    data = []
    [ data.append(i.to_json()) for i in host_list ]
    print data
    return render_template('saltstack/run_salt_cmd.html', data=data)
