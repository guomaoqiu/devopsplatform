# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: views.py
# @Date:   2018-02-01 17:47:45
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-02-07 18:57:43

from flask import render_template
from flask_login import login_required, request
from . import data
from dataapi import Graph

@data.route('/graphics_1',methods=['GET','POST'])
# @login_required
def graphics_1():
	if request.method == "POST":
		print Graph().graphics_1_api()
		return Graph().graphics_1_api()
	return render_template("graphics/graphics_1.html")
