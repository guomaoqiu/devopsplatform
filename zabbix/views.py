# -*- coding:utf-8 -*-
from flask import render_template, request, flash
from flask_login import login_required
import commands
from os import path
from werkzeug.utils import secure_filename

from app.scripts.zabbixapi import ZabbixAction
from . import zabbix

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
            flash(u' Upload file & import host to zabbix success!')
            z_add = ZabbixAction()
            z_add.login()
            z_add.create_hosts(path.join(upload_path,secure_filename(result.filename)))
            res = (commands.getoutput('cat /tmp/cache_add_zabbix.txt')).decode('utf-8').split('!')
            return render_template('new_zabdel.html',result=res)
        else:
            flash(u'务必选择一个文件进行操作!', 'danger')
            return render_template('new_zabadd.html')
    return render_template('new_zabadd.html')

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
        return  render_template('new_zabdel.html')
      z_del = ZabbixAction()
      z_del.login()
      z_del.delete_host(server_list)
      res = (commands.getoutput('cat /tmp/cache_delete_zabbix.txt')).decode('utf-8').split('!')
      return render_template('new_zabdel.html', result=res)
    return render_template('new_zabdel.html')