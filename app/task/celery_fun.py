# -*- coding:utf-8 -*-
import commands
from flask import jsonify, render_template, request, Response, flash
from app import celery
from flask_login import login_required
from app import celery
from . import task
import json, requests
###########################  后台执行任务公共配置 START ###########################

@task.route('/execute_task/<exclude_env>', methods=['GET', 'POST'])
@login_required
def execute_task(exclude_env):
    """
    @summary: 请求函数入口
    """
    #在执行任务之前检查Celery进程是否存在。
    result = commands.getoutput("ps -ef | grep celery | grep -v grep")
    if not result:
        return jsonify({"result":False,"message":u'未发现Celery进程，请检查该服务是否正常启动'})

    if exclude_env == "update_cbt_resource":
        task = update_cbt_resource.apply_async()
    elif exclude_env == "update_online_resource":
        task = update_online_resource.apply_async()
    else:
        pass

    data = {
        "task_id": task.id,
        "task_status": task.status
    }
    #print json.dumps(data)
    string = ''
    print '返回信息: ',data
    result = {"result":True,"data":data,"message":u'执行开始'}
    return jsonify(result)


@task.route('/task_result', methods=['GET', 'POST'])
@login_required
def task_result():
    '''
    @note: 通过task_id 来获取任务状态
    '''
    from flask import request
    print request.method
    task_id = json.loads(request.form.get('data'))['task_id']

    the_task = update_cbt_resource.AsyncResult(task_id)

    print("任务：{0} 当前的 state 为：{1}".format(task_id, the_task.state))

    if  the_task.state  == 'PROGRESS':
        print the_task.info.get('i', 0)
        result = {'state': 'progress','progress':0,"result_data":the_task.result}
    elif  the_task.state  == 'SUCCESS':
        result = {'state': "success", 'progress':100,"result_data":the_task.result}
    elif  the_task.state  == 'PENDING':
        result = {'state': 'waitting', 'progress':0,"result_data":the_task.result}
    elif  the_task.state  == 'REVOKED':
        result = { 'state': 'revoke', 'progress':0 }
        print the_task.result
    else:
        result = {'state': the_task.state,'progress':0,"result_data":the_task.result}
    return jsonify(result)

@task.route('/cancel_task/', methods=['GET', 'POST'])
@login_required
def cancel_task():
	task_id = json.loads(request.form.get('data'))['task_id']
	try:
		celery.control.revoke(task_id, terminate=True, signal='SIGKILL')
		return Response(json.dumps({'result':True,"message": "取消任务完成" }), mimetype='application/json')
	except Exception,e:
		return Response(json.dumps({'result': True, "message": u'取消任务失败.{0}'.format(e)}), mimetype='application/json')
	


@task.route('/task_history', methods=['GET', 'POST'])
@login_required
def task_history():
	# 需要启动flower
	# celery  flower --address=127.0.0.1 --port=5003 --broker=redis://127.0.0.1:6379/0
    data = []
    try:
        bad_r = requests.get('http://127.0.0.1:5003')
        if bad_r.status_code != 200:
            flash("Celery Flower访问失败","danger")
            return render_template('task_history.html',data=data)
    except Exception,e:
        flash(e,"danger")
        return render_template('task_history.html',data=data)
    FLOWER_ULR="http://127.0.0.1:5003/api/tasks"
    result=requests.get(url=FLOWER_ULR)
    #print dict(result)
    
    s = dict(json.loads(result.content))
    for k,v in s.items():
        data.append(v)
    return render_template('task_history.html',data=data)

###########################  后台执行任务公共配置 END  ###########################


###########################  任务绑定 ##################

@celery.task(bind=True)
def update_cbt_resource(self):
    '''
    @note: 任务进度
    '''	
    # 执行热更资源脚本，处理后获取版本号
    result=commands.getoutput("sleep 10 && echo 'ok'")
    print result
    return result
###########################  任务绑定 ##################


