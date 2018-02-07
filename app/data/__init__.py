# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: __init__.py
# @Date:   2018-02-01 17:42:48
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-02-07 18:29:22

from flask import Blueprint
data = Blueprint('data', __name__)

from . import views
