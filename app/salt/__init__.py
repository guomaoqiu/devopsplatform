# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: __init__.py
# @Date:   2018-03-30 14:44:19
# @Last Modified by:   guomaoqiu@sina.com
# @Last Modified time: 2018-04-13 15:31:37
from flask import Blueprint
salt = Blueprint('salt', __name__)

from . import views
