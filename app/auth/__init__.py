# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: __init__.py
# @Date:   2018-02-07 11:14:46
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-02-07 11:15:01

from flask import Blueprint

auth = Blueprint('auth', __name__)

import forms, views, error
