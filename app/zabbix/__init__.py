# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: __init__.py
# @Date:   2018-04-24 10:44:21
# @Last Modified by:   guomaoqiu@sina.com
# @Last Modified time: 2018-04-24 15:28:10
from flask import Blueprint

zabbix = Blueprint('zabbix', __name__)

from . import views, zabbixapi
