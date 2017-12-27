from flask import Blueprint
salt = Blueprint('salt', __name__)

from . import views
