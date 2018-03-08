# -*- coding:utf-8 -*-

# 用于在提交代码时触发该web应用然后pull代码
from flask import Flask, request, jsonify,abort
import git, os

code_dir = "./code"
git_url = "git@192.168.1.105:guomaoqiu/devopscode.git"


allow_ip=["192.168.1.105"]
app = Flask(__name__)

@app.route('/pullcode', methods=['POST'])
def pullcode():
    # 只允许指定服务器向Flask应用发起POST请求，否则直接返回403
    if request.headers.get('X-Forwarded-For', request.remote_addr) not in allow_ip:
        return abort(403)

    if request.method == 'POST':
        if os.path.isdir(code_dir):
            local_repo = git.Repo(code_dir)
            try:
                print local_repo.git.pull()
                # 重新加载代码
                #os.system("supervisorctl -c /etc/supervisord.conf restart devops && supervisorctl -c /etc/supervisord.conf restart celery")
                return jsonify({"result":True,"message":"pull success"})
            except Exception,e:
                return jsonify({"result":False,"message": "pull faild".format(e)})
        else:
            try:
                print git.Repo.clone_from(url=git_url, to_path=code_dir)
                return jsonify({"result":True,"message":"clone success"})
            except Exception, e:
                return jsonify({"result":False,"message": "clone faild".format(e)})
if __name__ == '__main__':
    app.run(host='192.168.1.200', port=5003)

