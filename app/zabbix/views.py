# -*- coding:utf-8 -*-
from flask import render_template, request, flash
from flask_login import login_required
import commands
from os import path
from werkzeug.utils import secure_filename
import json
#from app.scripts.zabbixapi import ZabbixAction

from . import zabbix
from zabbixapi import ZabbixAction
# zabbix server add
@zabbix.route('/zabbixadd' ,methods=['GET','POST'])
@login_required
def zabbixadd():
    if request.method == 'POST':
        result = request.files['file']
        #获取当前目录的位置然后通过path.join来连接上传目录
        basepath=path.abspath(path.dirname(__file__))
        upload_path = path.join(basepath,'upload')
        print upload_path
        #print '删除旧文件'
        if result.filename:
            result.save(path.join(upload_path,secure_filename(result.filename)))
            flash(u'文件上传成功 & 主机导入成功!','success')
            z_add = ZabbixAction()
            z_add.login_test()
            z_add.create_hosts(path.join(upload_path,secure_filename(result.filename)))
            res = (commands.getoutput('cat /tmp/cache_add_zabbix.txt')).decode('utf-8').split('!')
            return render_template('zabbixadd.html',result=res)
        else:
            flash(u'务必选择一个文件进行操作!', 'danger')
            return render_template('zabbixadd.html')
    return render_template('zabbixadd.html')

# zabbix server del
@zabbix.route('/zabbixdel',methods=['GET','POST'])
@login_required
def zabbixdel():
    if request.method == 'POST':
      server_list = []
      content = request.form['contenet'].split(',')

      print content
      for i in content:
        server_list.append(i.strip()) # i.strip() 去除多余的空格符
      if server_list[0] == '':
        flash(u'请填写至少一个或多个欲删除主机主机名!', 'danger')
        return  render_template('zabbixdel.html')
      z_del = ZabbixAction()
      z_del.login_test()
      print server_list
      z_del.delete_host(server_list)
      res = (commands.getoutput('cat /tmp/cache_delete_zabbix.txt')).decode('utf-8').split('!')
      return render_template('zabbixdel.html', result=res)
    return render_template('zabbixdel.html')

# 获取zabbix所有{主机:主机id}
@zabbix.route('/zabbix_host_get',methods=['GET','POST'])
@login_required
def zabbix_host_get():
      print 'xxxxx'
      host_get = ZabbixAction()
      host_get.login_test()
      host_get.get_host()
      return json.dumps(host_get.get_host()) 

# 获取zabbix所有{主机组:组id}
@zabbix.route('/zabbix_hostgruop_get',methods=['GET','POST'])
@login_required
def zabbix_hostgruop_get():
        hostgroup_get = ZabbixAction()
        hostgroup_get.login_test()
        hostgroup_get.get_host()
        return json.dumps(hostgroup_get.get_hostgruop()) 

# 获取zabbix主机组里面包含的主机，url后面直接跟组id
@zabbix.route('/zabbix_hostingruop_get/<groupid>',methods=['GET','POST'])
@login_required
def zabbix_hostingruop_get(groupid):
      print groupid
      host_in_group_get = ZabbixAction()
      host_in_group_get.login_test()
      return json.dumps(host_in_group_get.get_hostingroup(groupid)) 

@zabbix.route('/zabbix_get_hostitemid/<hostids>',methods=['GET','POST'])
@login_required
def zabbix_get_hostitemid(hostids):
      print hostids
      client = ZabbixAction()
      client.login_test()
      return json.dumps(client.get_host_item_id(hostids)) 


# 获取item历史记录, limit指定查询的历史条目数
@zabbix.route('/zabbix_get_history/<itemids>/<limit>',methods=['GET','POST'])
@login_required
def zabbix_get_history(itemids,limit):
      client = ZabbixAction()
      client.login_test()
      res = json.dumps(client.get_host_history(itemids,limit)) 
      return res

@zabbix.route('/testgr')
def testgr():
    return render_template('data3.html')




@zabbix.route('/data')
def data():
    arr = {}
    import time, random
    curr_time = int(round(time.time() * 1000)) 
    
    #http://127.0.0.1:5000/zabbix_get_history/68362/5

    arr['data_1'] = [[curr_time , random.randint(0,1)]]
    arr['data_2'] = [[curr_time , random.randint(0,1)]]
    # arr['data_3'] = [[curr_time , random.randint(0,99)]]

    client = ZabbixAction()
    client.login_test()
    res = client.get_host_history(itemids="68362",limit="100")
    for i in res:
        arr['data_3'] = [[int(i["clock"]) * 1000 , float(i['value'])]]
    print arr
    return json.dumps(arr)


@zabbix.route('/haha')
def haha():
    client=ZabbixAction()
    if client.login_test():
      return "认证成功"
    else:
      return "认证失败"


