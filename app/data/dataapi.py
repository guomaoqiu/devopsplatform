# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: dataapi.py
# @Date:   2018-02-07 17:53:34
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-02-07 18:46:27

import json, random

class Graph(object):
	"""docstring for Graph"""
	def __init__(self):
		pass


	def graphics_1_api(self):
	    
	    r1 = random.randint(0, 9)
	    r2 = random.randint(0, 9)
	    r3 = random.randint(0, 9)
	    data = {
	        "legen":["Chrome",'Firefox','IE10'],
	        "series":[r1,r2,r3]
	    }
	    print data
	    data=json.dumps(data, indent=4 ,encoding='utf-8')
	    return  data

