# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: views.py
# @Date:   2018-02-08 16:55:13
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-03-06 16:44:03
# jsonify 用于返回jsons数据
from flask import Flask, render_template,redirect,request,Response,flash,jsonify,url_for,current_app
from sqlalchemy import desc
from . import main
from flask_login import current_user, login_required
from ..decorators import admin_required , permission_required
import json,commands,datetime,sys,os
from .forms import  EditProfileForm, EditProfileAdminForm, ApiForm, DataForm,ResDataForm, EditorUidForm, EditorForm, DataFormOnline,ResDataFormOnline,AccessForm, WebsshForm,UidForm
from ..models import User, LoginLog, Role, ApiMg, AccessIpList, Hostinfo, RuncmdLog
from .. import db
from app.crypto import prpcrypt
import time,os,requests
from hashlib import md5
from ..salt.saltapi import SaltApi
from app import celery
from ..email import send_email
from app.auth.forms import RegistrationForm
from ..zabbix.zabbixapi import ZabbixAction
from celery.task.control import revoke

reload(sys)
sys.setdefaultencoding("utf-8")

###############################################################################

@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    '''
    @note: 在登陆状态下只允许管理者进入，否则来到403禁止界面
    '''
    return render_template('admin.html')

###############################################################################

@main.route('/')
# @admin_required
@login_required
def index():
    '''
    @note: 返回主页内容
    '''
    if not current_user.is_authenticated:
        return redirect('auth/login')
    else:
        return render_template('index.html')

###############################################################################

@main.route('/page_403')
# @admin_required
@login_required
def page_403():
    '''
    @note: 返回主页内容
    '''
    if not current_user.is_authenticated:
        return redirect('auth/login')
    else:
        return render_template('403.html')

###############################################################################

@main.route('/page_404')
# @admin_required
@login_required
def page_404():
    '''
    @note: 返回主页内容
    '''
    if not current_user.is_authenticated:
        return redirect('auth/login')
    else:
        return render_template('404.html')  
###############################################################################

@main.route('/page_500')
# @admin_required
@login_required
def page_500():
    '''
    @note: 返回主页内容
    '''
    if not current_user.is_authenticated:
        return redirect('auth/login')
    else:
        return render_template('500.html') 

###############################################################################

@main.route('/building')
# @admin_required
@login_required
def building():
    '''
    @note: 返回主页内容
    '''
    if not current_user.is_authenticated:
        return redirect('auth/login')
    else:
        return render_template('building.html')         

###############################################################################

@main.route('/user/<username>')
def user(username):
    '''
    @note: 返回用户信息页面
    '''
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

###############################################################################

@main.route('/usermanager',methods=['GET', 'POST'])
@login_required
def usermanager():
    '''
    @note: 用户管理
    '''
    # 列出用户
    user = User.query.all()
    data = []

    for each_user in user:
        data.append(each_user.to_json())
    print data
    form = RegistrationForm()
    if form.validate_on_submit():
        #检查config.py中定义的公司邮箱后缀名
        if current_app.config['COMPANY_MAIL_SUFFIX'] != str(form.email.data).split('@')[1]:
            flash('严禁使用非公司邮箱进行注册操作!', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '账户确认','auth/email/confirm', user=user, token=token)
        flash('已通过电子邮件向注册用户发送确认电子邮件.','info')
    return render_template('user_manager.html',data=data,form=form)

###############################################################################
@main.route('/platform_log')
@login_required
def platform_log():
    '''
    @note: 平台日志
    '''
    # 登陆日志
    loginlog = LoginLog.query.order_by(desc(LoginLog.id)).all() # 查询所有
    login_log_data = []
    for each_log in loginlog:
        login_log_data.append(each_log.to_json())
    
    #命令执行日志
    rumcmd_log_data = []
    rumcmdlog = RuncmdLog.query.order_by(desc(RuncmdLog.id)).all()
    for each_log in rumcmdlog:
        rumcmd_log_data.append(each_log.to_json())

    return render_template('platform_log.html',
                            login_log_data=login_log_data,
                            rumcmd_log_data=rumcmd_log_data)

###############################################################################
@main.route('/server_list')
@login_required
def server_list():
    '''
    @note: 主机列表
    '''
    host_list = Hostinfo.query.all()
    data = []
    [ data.append(i.to_json()) for i in host_list ]
    return render_template('server_list.html',data=data)

###############################################################################

@main.route('/display_hostdetail/<hostname>')
@login_required
def display_hostdetail(hostname):
    '''
    @note: 获取传递过来主机的信息信息
    '''
    
    host_list = Hostinfo.query.filter_by(hostname=hostname).first()
    print host_list.to_json()
    client = SaltApi()
    params = {'client': 'local', 'fun': 'test.ping', 'tgt': hostname }
    json_data = client.get_allhostname(params)
    data = dict(json.loads(json_data)['return'][0])
    if data.values()[0]:
        host_status = True
        return render_template("server_info.html",data = host_list.to_json(),host_status=host_status)

###############################################################################
@main.route('/get_server_info',methods=['GET', 'POST'])
def get_server_info():
    '''
    @note: 通过saltapi获取所有minion主机的服务器信息写入数据库中
    '''
    # 获取所有server的hostname
    if request.method == "POST":
        if not ApiMg.query.filter_by(app_name='saltstackapi').first():
            result = {"result": False, "message": u'请确保API信息已录入！'}
            return jsonify(result)
        else:

            try:
                client = SaltApi()
                params = {'client': 'local', 'fun': 'test.ping', 'tgt': '*'}
                json_data = client.get_allhostname(params)
                data = dict(json.loads(json_data)['return'][0])
                print data
                hostname_list = []

                [hostname_list.append(i) for i in data.keys()]
                #print hostname_list
                for host in hostname_list:
                    if not Hostinfo.query.filter_by(hostname=host).first():

                        all_host_info = dict(client.get_minions(host).items())
                        print all_host_info
                        host_record = Hostinfo(
                            hostname=all_host_info['hostname'],
                            private_ip=all_host_info['private_ip'],
                            external_ip=all_host_info['external_ip'],
                            mem_total=all_host_info['mem_total'],
                            cpu_type=all_host_info['cpu_type'],
                            num_cpus=all_host_info['num_cpus'],
                            os_release=all_host_info['os_release'],
                            kernelrelease=all_host_info['kernelrelease']
                        )
                        db.session.add(host_record)
                        db.session.commit()
                                                                                       
                result = {"result": True, "message": u'刷新完毕！'}
                return jsonify(result)

            except Exception, e:
                print e
                result = {"result": False, "message": u'刷新出错！{0}'.format(e)}
                return jsonify(result)

###############################################################################

@main.route('/delete_server',methods=['GET', 'POST'])
def delete_server():
    '''
    @note: 从数据库中删除已经存在的主机
    '''
    delete_host = []
    hostname = json.loads(request.form.get('data'))['hostname']
    [ delete_host.append(host.encode('raw_unicode_escape')) for host in hostname.split(',')]
    try:
        [ db.session.query(Hostinfo).filter(Hostinfo.hostname == host).delete() for host in delete_host ]
        result = {'result': True, 'message': u"删除所选主机成功" }
    except Exception, e:
        result = {'result': False, 'message': u"删除所选主机失败,%s" % e}
    return jsonify(result)

###############################################################################

@main.route('/access_iplist',methods=['GET', 'POST'])
@login_required
def access_iplist():
    '''
    @note: 主机列表
    '''
    form = AccessForm()
    if form.validate_on_submit():
        print current_user.name
        #current_user.name = form.name.data
        c = AccessIpList()
        c.create_user = current_user.name
        c.remark = form.remark.data
        c.ip = form.ip.data
        db.session.add(c)
        return redirect(url_for('.access_iplist'))
    ip = AccessIpList.query.all()
    data = []
    [ data.append(i.to_json()) for i in ip ]
    print data
    if request.method == 'POST':
        check_id = json.loads(request.form.get('data'))['check_id']
        del_ip = AccessIpList.query.filter_by(id=check_id).first()
        try:
            db.session.delete(del_ip)
            print check_id
            return  jsonify({"result":True,"message":"访问IP删除成功"})
        except Exception, e:
            db.session.rollback()
            print e
            return  jsonify({"result":False,"message":"访问IP删除失败".format(e)})
    return render_template('access_iplist.html',form=form,data=data)

###############################################################################

@main.route('/loginlog',methods=['GET', 'POST'])
@login_required
def loginlog():
    '''
    @note: 查询登录日志
    '''
    if request.method == 'POST':
        return "ok"
        #return redirect('http://www.baidu.com')
    # 以ID 倒序查询 最近10条
    #res = LoginLog.query.order_by(desc(LoginLog.id)).limit(10)
    res = LoginLog.query.order_by(desc(LoginLog.id)).all() # 查询所有
    data = []
    for x in res:
        data.append(x.to_json())
    #user_list = User.query.all()#
    return render_template('loginlog.html',data=data)

###############################################################################

@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    '''
    @note: 普通用户编辑
    '''
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.','success')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

###############################################################################

@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    '''
    @note: 管理员编辑
    '''
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.','success')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)

###############################################################################

# 平台业务逻辑
@main.route('/api_manager',methods=['GET', 'POST'])
@login_required
def api_manager():
    '''
    @note: 对接第三方API管理函数
    '''
    form = ApiForm()
    #i#f form.validate_on_submit():
    if form.validate_on_submit():
        apiinfo = ApiMg(app_name=form.app_name.data,
                    api_user=form.api_user.data,
                    api_paas=form.api_paas.data,
                    api_url=form.api_url.data)
        try:
            # 加密api密码
            prpcrypt_key = prpcrypt(current_app.config.get('PRPCRYPTO_KEY'))
            apiinfo.api_paas = prpcrypt_key.encrypt(form.api_paas.data)
            db.session.add(apiinfo)
            db.session.commit()
            flash('添加Api信息成功','success')
        except Exception,e:
            db.session.rollback()
            print e
            flash('添加Api信息错误 %s' % e ,'danger')
    res = ApiMg.query.all()
    data = []
    for each_data in res:
        data.append(each_data.to_json())

    return render_template('api_manager.html',form=form,data=data)
###############################################################################

# delete api
@main.route('/api_manager_del',methods=['GET', 'POST'])
@login_required
def api_manager_del():
    '''
    @note: 在登陆状态下只允许管理者进入，否则来到403禁止登陆界面
    '''
    if request.method == 'POST':
        check_id = json.loads(request.form.get('data'))['check_id']
        api_id = ApiMg.query.filter_by(id=check_id).first()
        try:
            db.session.delete(api_id)
            print check_id
            return  jsonify({"result":True,"message":"删除成功"})
        except Exception, e:
            db.session.rollback()
            print e
            return  jsonify({"result":False,"message":"删除失败".format(e)})

# test api
@main.route('/apitest', methods=['GET', 'POST'])
#@login_required
def apitest():
    '''
    @note: 在登陆状态下只允许管理者进入，否则来到403禁止登陆界面
    '''
    if request.method == 'POST':
        # 前端获取应用API的名称，然后数据库中获取api应用名称，最后然后通过不同API应用的登录方式去检查是否是正常连接
        check_id = json.loads(request.form.get('data'))["check_id"]
        app_name = str(ApiMg.query.filter_by(id=check_id).first())

        if app_name == "zabbixapi":
            client = ZabbixAction()
            if client.login_test():
                return jsonify({"result": True, "message": "%s 连接正常" % app_name})
            else:
                return jsonify({"result": False, "message": "%s 连接异常,请检查API信息是否正确" % app_name})
        elif app_name == "saltstackapi":
            client = SaltApi()
            if client.login_test():
                return jsonify({"result": True, "message": "%s 连接正常" % app_name })
            else:
                return jsonify({"result": False, "message": "%s 连接异常,请检查API信息是否正确" % app_name})
        elif app_name == "":
            pass
        else:
            pass

###############################################################################
# 导入数据库
@main.route('/import_data', methods=['GET', 'POST'])
@login_required
def import_data():
    '''
    @note: 数据导入导出(jptest-->jpcbt)
    '''
    form = DataForm()
    if form.validate_on_submit():
        data_content = form.data_content.data
        client_version = form.client_version.data
        if not data_content or not client_version:
            flash('表名称或客户端版本号为空','danger')
            return render_template('import_data.html',form=form)
        else:
            # 执行导入脚本后的输出结果
            input_result = commands.getoutput("ssh jp-cbt '/bin/bash /root/import_from_jptest_to_jpcbt.sh %s'" % data_content)
            #input_result = commands.getoutput("date")
            # 生成数据版本号
            new_dataversion = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            #print new_dataversion
            # on cbt_server
            dataversion_result_oncbt = commands.getoutput("ssh jp-cbt '/bin/bash -x /usr/local/process_version_japan/modify_online_for_cbt_oncbt.sh %s'" % (int(new_dataversion)))
            # on jpcontorl_server
            #print client_version, new_dataversion
            dataversion_result = commands.getoutput("/bin/bash -x /usr/local/process_version_japan/modify_online_for_cbt.sh %s %s" % (client_version,int(new_dataversion)))
            print dataversion_result

            flash(u'导入完毕!','success')
            #return redirect(url_for('.import_data',form=form,new_dataversion=new_dataversion))
            return render_template('import_data.html',
                                    form=form,
                                    input_result=input_result,
                                    dataversion_result_oncbt=dataversion_result_oncbt,
                                    dataversion_result=dataversion_result
                                    )

    return render_template('import_data.html',form=form)


# CBT热更
@main.route('/cbt_resource', methods=['GET', 'POST'])
@login_required
def cbt_resource():
    '''
    @note: cbt热更
    '''
    form = ResDataForm()
    if form.validate_on_submit():
        res_version = form.res_version.data
        client_version = form.client_version.data
        if not res_version or not client_version:
            flash('表名称或客户端版本号为空','danger')
            return render_template('update_cbt_resource.html',form=form)
        else:

            # 生成数据版本号
            new_dataversion = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            # on cbt_server
            resversion_result_oncbt = commands.getoutput("ssh jp-cbt '/bin/bash -x /usr/local/process_version_japan/modify_online_for_cbt_oncbt.sh %s %s'" % (int(new_dataversion), int(res_version)))
            # on jpcontorl_server

            resversion_result = commands.getoutput("/bin/bash -x /usr/local/process_version_japan/modify_online_for_cbt.sh %s %s %s" % (client_version,int(new_dataversion),int(res_version) ))
            #print dataversion_result

            flash(u'更新完毕','success')

            return render_template('update_cbt_resource.html',
                                    form=form,
                                    resversion_result_oncbt=resversion_result_oncbt,
                                    resversion_result=resversion_result
                                    )
    return render_template('update_cbt_resource.html',form=form)

############ 线上配置修改 Start ###########
@main.route('/import_data_online', methods=['GET', 'POST'])
@login_required
def import_data_online():
    '''
    @note: 线上数据导入导出(jpcbt-->线上)
    '''
    form = DataFormOnline()
    if form.validate_on_submit():
        data_content = form.data_content.data
        #client_version = form.client_version.data
        if not data_content:
            flash('表名称不能为空','danger')
            return render_template('import_data_online.html',form=form)
        else:
            # 执行导入脚本后的输出结果
            #input_result = commands.getoutput("ssh jp-cbt '/bin/bash /root/import_from_jpcbt_to_jpserver.sh %s'" % data_content)
            input_result = commands.getoutput("date")
            print input_result
            # 生成数据版本号
            new_dataversion = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            print new_dataversion

            dataversion_result_online = commands.getoutput("/bin/bash -x /usr/local/process_version_japan/modify_online_config_for_all.sh %s" % (int(new_dataversion)))
            # on jpcontorl_server
            print dataversion_result_online

            flash(u'导入完毕!','success')
            #return redirect(url_for('.import_data',form=form,new_dataversion=new_dataversion))
            return render_template('import_data_online.html',
                                    form=form,
                                    input_result=input_result,
                                    dataversion_result_online=dataversion_result_online
                                    )

    return render_template('import_data_online.html',form=form)

# 正式服热更(后台任务)
@celery.task(bind = True)
def update_online_resource(self):
    '''
    @note: 任务进度
    '''
    # 执行热更资源脚本，处理后获取版本号
    esult=commands.getoutput("echo test")
    #result=commands.getoutput("/bin/bash /root/public_update_jp_hot.sh.sh > /tmp/online_resource.txt && tail -1 /tmp/online_resource.txt")
    return result

# 正式服热更(修改配置)
@main.route('/online_resource', methods=['GET', 'POST'])
@login_required
def online_resource():
    '''
    @note: 正式服热更(数据版本号，热更版本号)
    '''
    form = ResDataFormOnline()
    if form.validate_on_submit():
        res_version = form.res_version.data
        if not res_version:
            flash('热更版本号不能为空','danger')
            return render_template('update_online_resource.html',form=form)
        else:
            # 生成数据版本号
            new_dataversion = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
            #resversion_result = res_version
            resversion_result = commands.getoutput("/bin/bash -x /usr/local/process_version_japan/modify_online_config_for_all.sh %s %s" % (int(new_dataversion),int(res_version) ))

            flash(u'更新完毕','success')

            return render_template('update_online_resource.html',
                                    form=form,
                                    resversion_result=resversion_result
                                    )
    return render_template('update_online_resource.html',form=form)

@main.route('/updatecode_online',methods=['GET', 'POST'])
@login_required
def updatecode_online():
    '''
    @note: 代码更新
    '''
    if request.method == 'POST' and current_user.is_administrator:
        try:
            #result = commands.getoutput('''date''')
            result = commands.getoutput('''ssh jp-cbt "sh /root/update_online_code.sh"''')
            print result
            #return  render_template('updatecode.html',result=result)
            return Response(json.dumps({'result':True,"message": "更新完毕" }), mimetype='application/json')
        except Exception,e:
            #return  render_template('updatecode.html',result=result)
            return Response(json.dumps({'result': True, "message": u'更新失败.{0}'.format(e)}), mimetype='application/json')
    return  render_template('updatecode_online.html')
############ 线上配置修改  End  ###########

# 配置回滚
@main.route('/rollback', methods=['GET', 'POST'])
@login_required
def rollback():
    if request.method == "POST":
        # cbt服务器
        os.system("ssh jp-cbt '/bin/bash -x /usr/local/process_version_japan/rollback.sh")
        # 控制服务器
        #os.system('date')
        os.system("/bin/bash -x /usr/local/process_version_japan/rollback.sh")

        return jsonify({ "result":True,"message": "回滚完毕~~~" })


############################################################

@main.route('/settime', methods=['GET', 'POST'])
@login_required
def settime():
    '''
    @note: cbt服务器时间设定
    '''
    if request.method == 'POST':
        data = request.get_json()['time']
        print data
        try:
            commands.getoutput(''' ssh shipcbt "date -s '%s'" ''' % data)
            return Response(json.dumps({'result':True,"message":u'设置成功'}), mimetype='application/json')
        except Exception,e:
            return Response(json.dumps({'result': True, "message": u'设置失败。{0}'.format(e)}), mimetype='application/json')
    #else:
        #return redirect(index)
    current_tiem = commands.getoutput('''ssh shipcbt "date +%F\ %T" ''')
    return render_template('settime.html',current_tiem=current_tiem)

############################################################

@main.route('/clean_cache',methods=['GET', 'POST'])
@login_required
def clean_cache():
    '''
    @note 缓存清理
    '''
    # action = ''
    result = commands.getoutput('''ssh  shipcbt "/bin/bash /root/switch_register.sh check" ''')
    if request.method == 'POST':
        try:
            # gm
            commands.getoutput('''ssh shipcbt "sh /root/clean_cache_gm.sh"''')
            # game
            commands.getoutput('''ssh shipcbt "sh /root/clean_cache.sh"''')
            return Response(json.dumps({'result':True,"message":u'清理完毕'}), mimetype='application/json')
        except Exception,e:
            return Response(json.dumps({'result': True, "message": u'清理失败.{0}'.format(e)}), mimetype='application/json')
    return  render_template('cleancache.html', result=result)

############################################################

@main.route('/updatecode',methods=['GET', 'POST'])
@login_required
def updatecode():
    '''
    @note: 代码更新
    '''
    if request.method == 'POST':
        try:
            #result = commands.getoutput('''date''')
            result = commands.getoutput('''ssh jp-cbt "sh /root/update_code.sh"''')
            print result
            #return  render_template('updatecode.html',result=result)
            return Response(json.dumps({'result':True,"message": "更新完毕" }), mimetype='application/json')
        except Exception,e:
            #return  render_template('updatecode.html',result=result)
            return Response(json.dumps({'result': True, "message": u'更新失败.{0}'.format(e)}), mimetype='application/json')
    return  render_template('updatecode.html')

############################################################

########## 维护/开服 ########

@main.route('/maintain',methods=['GET', 'POST'])
@login_required
def maintain():
    '''
    @note 停机维护 (限制管理员操作)
    '''
    if request.method == 'POST' and current_user.is_administrator:
        try:
            commands.getoutput('''sh /root/maintain.sh''')
            result=commands.getoutput('''grep "APP_STATUS" /srv/salt/warship/files/game_config/warship/config/version.jp.warshipgirls.com/config.php | grep -v  "DEV"''')
            #result=commands.getoutput('date')
            return Response(json.dumps({'result':True,"message":u'维护脚本执行完毕',"res":result }), mimetype='application/json')
        except Exception,e:
            return Response(json.dumps({'result': True, "message": u'维护脚本执行失败.{0}'.format(e),"res":result}), mimetype='application/json')
    return  render_template('maintain.html')
############################################################
@login_required
@main.route('/openservice',methods=['GET', 'POST'])
def openservice():
    '''
    @note 开服操作 (限制管理员操作)
    '''
    if request.method == 'POST' and current_user.is_administrator:
        try:
            commands.getoutput('''sh /root/open.sh''')
            result=commands.getoutput('''grep "APP_STATUS" /srv/salt/warship/files/game_config/warship/config/version.jp.warshipgirls.com/config.php | grep -v  "DEV"''')
            #time.sleep(10)
            return Response(json.dumps({'result':True,"message":u'开服脚本执行完毕',"res":result}), mimetype='application/json')
        except Exception,e:
            return Response(json.dumps({'result': True, "message": u'开服脚本执行失败.{0}'.format(e),"res":result}), mimetype='application/json')
    #return  render_template('openservice.html')

############################################################

@main.route('/webssh',methods=['GET', 'POST'])
@login_required
def webssh():
    form = WebsshForm()
    if form.validate_on_submit():
        data = {
            "host":form.host.data,
            "port":form.port.data,
            "username":form.username.data,
            "password":form.password.data,
        }
        return render_template('webssh.html',form=form,data=data)
        print data
    return  render_template('webssh.html',form=form)
############################################################


@main.route('/addallowuid',methods=['GET', 'POST'])
@login_required
def addallowuid():
    white_data = commands.getoutput(''' ssh shipcbt "cat /data/warship/config/cbt.jianniang.com/uidList.php" ''')
    fixed_data = commands.getoutput('''ssh shipcbt "cat /data/warship/config/cbt.jianniang.com/fixed_data_uid" ''')
    form = UidForm()
    if form.validate_on_submit():
        content = form.uid_content.data
        print content
        if len(content) == 0 :
            flash(u'UID不能为空! ','danger')
        else:
            try:
                res = commands.getoutput('''ssh shipcbt "/bin/bash /root/add_allowuid.sh %s"''' % content )
                print res
                flash(u'UID添加完毕，手动刷新页面！','success')
                return redirect(url_for("main.addallowuid"))
            except Exception,e:
                flash(u'UID添加失败,请联系管理员!\n {0}'.format(e),'danger')
                return render_template('add_allowuid.html',form=form,white_data=white_data,fixed_data=fixed_data)
    return  render_template('add_allowuid.html', form=form,white_data=white_data,fixed_data=fixed_data)

############################################################

@main.route('/uideditor',methods=['POST', 'GET'])
@login_required
def uideditor():
    file_path = "/tmp/uidList.php"
    remote_dir = "shipcbt:/data/warship/config/cbt.jianniang.com/uidList.php"
    form = EditorUidForm()
    if form.validate_on_submit():
        param_do = form.do_action.data
        if param_do == "read":
            os.system("scp %s /tmp/" % remote_dir)
            with open(file_path, 'rb') as f:
                file_data = f.read()
                f.closed
            form.file_data.data=file_data
            flash("【SUCCESS】: 文件读取成功", "success")
            return render_template('uideditor.html',
                                form=form,
                                file_path=file_path,
                                )
        if param_do == 'save':
            file = open(file_path, 'wb')
            print form.file_data
            file.write(form.file_data.data.replace('\r\n','\n'))
            file.close()
            os.system("scp %s %s" % (file_path,remote_dir))
            flash("【SUCCESS】: 提交成功", "success")
            return render_template('uideditor.html',
                                form=form,
                                file_path=file_path,
                                )
    return render_template('uideditor.html',form=form)


@main.route('/uideditor2',methods=['POST', 'GET'])
@login_required
def uideditor2():
    file_path = "/tmp/fixed_data_uid"
    remote_dir = "shipcbt:/data/warship/config/cbt.jianniang.com/fixed_data_uid"
    #os.system("scp root@192.168.56.127:/data/warship/config/version.jr.moefantasy.com/ipList.php /tmp/")
    form = EditorUidForm()
    if form.validate_on_submit():
        param_do = form.do_action.data
        if param_do == "read":
            os.system("scp %s /tmp/" % remote_dir)
            with open(file_path, 'rb') as f:
                file_data = f.read()
                f.closed
            form.file_data.data=file_data
            flash("【SUCCESS】: 文件读取成功", "success")
            return render_template('uideditor2.html',
                                form=form,
                                file_path=file_path,
                                )
        if param_do == 'save':
            file = open(file_path, 'wb')
            print form.file_data
            file.write(form.file_data.data.replace('\r\n','\n'))
            file.close()
            os.system("scp %s %s" % (file_path,remote_dir))
            flash("【SUCCESS】: 提交成功", "success")
            return render_template('uideditor2.html',
                                form=form,
                                file_path=file_path,
                                )
    return render_template('uideditor2.html',form=form)
############################################################



@main.route('/cleanuid',methods=['POST', 'GET'])
@login_required
def cleanuid():
    if request.method == 'POST':
        # (rescode 命令执行状态码, res 命令执行结果)
        #rescode,res = commands.getstatusoutput('date')
        #print rescode,res
        rescode,res = commands.getstatusoutput('''ssh  shipcbt "sed  -i '3d' /data/warship/config/cbt.jianniang.com/uidList.php" ''')
        if rescode == 0:
            return Response(json.dumps({'result':True,"message":u'清空完毕'}))
        else:
            return Response(json.dumps({'result': True, "message": u'清空失败.{0}'.format(res)}))



############################################################

# @main.route('/test',methods=['POST', 'GET'])
# # @login_required
# def test():
#     if request.method == 'POST':
#         print request.method
#     else:
#         print request.method
#     return "方法为: %s " % request.method

############################################################

@main.route('/editor',methods=['POST', 'GET'])
@login_required
def editor():
    form = EditorForm()
    if form.validate_on_submit():
        param_do = form.do_action.data
        print param_do
        file_path = form.file_path.data
        (file_stat_code,file_stat) = commands.getstatusoutput("stat %s " % file_path)
        if param_do == "read":

            # 判断文件是否存在
            if not os.access(file_path, os.F_OK):
                #print file_stat_dis
                flash("【ERROR:】该文件 %s 不存在" % file_path,"danger")
                return render_template('editor.html',
                                        form=form,
                                        file_path=file_path,
                                        file_stat=file_stat,
                                        file_stat_dis=False
                                        )
            # 判断文件是否可读
            elif not os.access(file_path, os.R_OK):
                flash("【ERROR:】该文件 %s 不可读" % file_path,"danger")
                return render_template('editor.html',
                                        form=form,
                                        file_path=file_path,
                                        file_stat=file_stat,
                                        file_stat_dis=False
                                        )
            # 判断文件是否可写
            elif not os.access(file_path, os.W_OK):
                flash("【ERROR:】该文件 %s 只可读不可写" % file_path,"warning")
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    f.closed
                form.file_data.data=file_data
                return render_template('editor.html',
                                        form=form,
                                        file_path=file_path,
                                        file_stat=file_stat,
                                        file_stat_dis=True
                                        )
            #读取文件
            else:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    f.closed
                form.file_data.data=file_data
                return render_template('editor.html',
                                    form=form,
                                    file_path=file_path,
                                    file_stat=file_stat,
                                    file_stat_dis=True
                                    )
        # 保存文件
        if param_do == 'save':
            file_access = os.access(file_path, os.W_OK)
            if not file_access:
                flash("【ERROR:】该文件 %s 只可读不可写" % file_path,"danger")
                return render_template('editor.html',
                                        form=form,
                                        file_path=file_path,
                                        file_access=file_access,
                                        file_stat=file_stat,
                                        file_stat_dis=False
                                        )
            # 比较文件md5 如果相同则判断为文件未发生改变
            file_md5sum = md5(open(file_path, 'rb').read()).hexdigest()
            form_md5sum = md5(form.file_data.data.replace('\r\n','\n')).hexdigest()
            if file_md5sum == form_md5sum:
                flash("【NOTICE:】该文件 %s 未发生改变" % file_path,"info")
                return render_template('editor.html',
                                        form=form,
                                        file_path=file_path,
                                        file_access=file_access,
                                        file_stat=file_stat,
                                        file_stat_dis=True
                                        )
            # 文件备份
            postfix = time.strftime("%Y%m%d%H%M%S")
            file_backup = file_path + "." + postfix
            (rescode,result) = commands.getstatusoutput("cp -p {0} {1}".format(file_path,file_backup))

            if rescode == 0:
                # dos2unix
                commands.getoutput("dos2unix %s" % file_path)
                flash("【SUCCESS】: 成功保存修改并备份文件为:  %s" % file_backup,"success")
            else:
                flash("【ERROR:】该文件 %s 备份失败" % file_path,"danger")
            file = open(file_path, 'wb')
            file.write(form.file_data.data.replace('\r\n','\n'))
            file.close()

            return render_template('editor.html',
                                form=form,
                                file_path=file_path,
                                file_access=file_access,
                                file_stat=file_stat,
                                file_stat_dis=False
                                )
    return render_template('editor.html',form=form)

############################################################
# from celery.task import periodic_task
# from celery.schedules import crontab
# from ..salt.saltapi import SaltApi
# from ..zabbix.zabbixapi import ZabbixAction
# from flask import render_template, request

# @periodic_task(run_every=10)
# # '''
# # @note: 每10s执行一次这个任务函数

# # 设置周期性任务:
# # 1）直接设置秒数
# # 例如刚刚所说的10秒间隔，run_every=10，每10秒执行一次任务。1分钟即是60秒；1小时即是3600秒。
# # 2）通过datetime设置时间间隔
# # 1小时15分钟40秒 = 1*60*60 + 15*60 + 40。这种情况可读性也不高。
# # @periodic_task(run_every=datetime.timedelta(hours=1, minutes=15, seconds=40))
# # 3）celery的crontab表达式(教程:http://yshblog.com/blog/164)
# # '''
# # @celery.task(bind=True)
# def check_saltapi():
#     '''
#     @note:
#     '''
#     print 'ok'
