from flask import Blueprint
dataapi = Blueprint('dataapi', __name__)

from . import views
