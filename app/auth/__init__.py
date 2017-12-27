from flask import Blueprint

auth = Blueprint('auth', __name__)

import forms, views, error
