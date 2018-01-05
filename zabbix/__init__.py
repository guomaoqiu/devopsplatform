from flask import Blueprint

zabbix = Blueprint('zabbix', __name__)

from . import views
