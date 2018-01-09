# -*- coding:utf-8 -*-
import commands
from flask import jsonify, render_template, request, Response, flash
from app import celery
from flask_login import login_required
from app import celery
from . import task
import json, requests


@celery.task(bind=True)
def saltapi_check_task(self):
    """启动worker: celery -A test_celery.celery worker -B --loglevel=debug"""
    result=commands.getoutput("echo 'SaltstackApi正常'")
    print result
    return True

class Trigger(Task):
    def run(self):
        task = saltapi_check_task.apply_async()
        print task

trigger = Trigger()
trigger.run()



