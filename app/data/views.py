# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: views.py
# @Date:   2018-02-01 17:47:45
# @Last Modified by:   guomaoqiu@sina.com
# @Last Modified time: 2018-05-02 16:13:44

from flask import render_template
from flask_login import login_required, request
from . import data
from .. import db
import time
from ..models import DataApi
from dataapi import graphics_1_api, graphics_2_api
#########################
@data.route('/graphics_1',methods=['GET','POST'])
@login_required
def graphics_1():
	'''
	@note: 饼形图 
	POST: api发送post请求获取数据 
	GET: 用于测试/示例
	'''

	if request.method == "POST":
		print graphics_1_api()
		return graphics_1_api()
	return render_template("graphics/graphics_1.html")

# @data.route('/graphics_2',methods=['GET','POST'])
# # @login_required
# def graphics_2():
# 	'''
# 	@note: 饼形图 
# 	POST: api发送post请求获取数据 
# 	GET: 用于测试/示例
# 	'''
# 	tmp_time = 0   
#     '''
#     @note: 单曲线图
#     '''
#     global tmp_time
#     if tmp_time > 0:
#         ss = (db.session.query(DataApi).filter(DataApi.create_time > tmp_time/1000).all())
#         print "当前时间",time.time()
#     else:
#         ss = (db.session.query(DataApi).all())
#     data = []
#     for i in ss:
#         name =  int(i.to_json()["name"])
#         ctime =  int(time.mktime(time.strptime(str(i.to_json()['create_time']), "%Y-%m-%d %H:%M:%S")))
#         print name,ctime
#         data.append([name, ctime])

#     #print arr
#     print data
#     if len(data)>0:
#         tmp_time = data[-1][0]
#         print tmp_time

#     # if request.method == "POST":
    	

#     return json.dumps(data)