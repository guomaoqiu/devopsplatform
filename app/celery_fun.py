# -*- coding: utf-8 -*-
# from celer import Celery
import commands
from flask import jsonify
from app import celery


class MyCelery():

	def __init__(sele):
		pass

	def execute_task(self,task_name):
		result = commands.getoutput("ps -ef | grep celery | grep -v grep")
		if not result:
			return jsonify({"result":False,"message":u'未发现Celery进程，请检查该服务是否正常启动'})
		self.task = task_name.apply_async()	
		
		data = {
	        "task_id": self.task.id,
	        "task_status": self.task.status
	    }
		#print task_name
	 	#return 'xxx'
		return jsonify({"result":True,"data":data,"message":u'执行开始'})
