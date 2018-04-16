# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: decorators.py
# @Date:   2018-03-30 14:44:19
# @Last Modified by:   guomaoqiu@sina.com
# @Last Modified time: 2018-04-13 15:28:55

from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

# 装饰器函数,带参数，3层函数
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
    
# 调用上面装饰器函数
def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f) # 带参数，且传递函数