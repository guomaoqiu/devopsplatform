# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @Date:   2018-01-17 10:50:51
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-02-27 12:04:54
from flask import render_template
from . import auth

@auth.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@auth.app_errorhandler(500)
def internal_server_error(e):
	print 'xxxxxxxxxxxxxxx',e
    return render_template('500.html'), 500

@auth.app_errorhandler(403)
def forbbiden(e):
    return render_template('403.html'), 403