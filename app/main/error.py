# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @Date:   2018-02-01 14:39:05
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-02-07 11:42:59
from flask import render_template
from . import main

@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@main.app_errorhandler(403)
def forbbiden(e):
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404