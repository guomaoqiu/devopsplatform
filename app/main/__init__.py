# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @Date:   2018-01-17 10:50:53
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-02-07 11:42:28
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, error, forms

import app
from flask import Flask
app = Flask(__name__)



def mydate(time_str):
    result = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time_str))
    return result
app.jinja_env.filters['mydate'] = mydate
