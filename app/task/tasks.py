# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: tasks.py
# @Date:   2018-03-29 10:34:37
# @Last Modified by:   guomaoqiu@sina.com
# @Last Modified time: 2018-05-08 14:49:15
from app import celery

@celery.task(bind = True)
def testping(self):
	return "ok"