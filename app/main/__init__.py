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
