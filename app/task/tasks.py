# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: tasks.py
# @Date:   2018-03-29 10:34:37
# @Last Modified by:   guomaoqiu@sina.com
# @Last Modified time: 2018-03-29 10:40:56
from app import celery

@celery.task(bind = True)
def testping(self):
	print 'xx'
	return 'ok'