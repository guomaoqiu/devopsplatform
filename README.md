基础FlaskWeb后台代码。可基于该基础代码作为模板，进行其他开发作业
目前功能:
1. 用户注册、登录(邮件确认)
2. 通过用户权限进行页面视图限制
3. 第三个方API接入管理
4. 通过用户添加/设置IP地址进行访问限制
5. Celery后台任务执行,周期性任务执行


##### 0. 获取代码
```
cd /usr/local/
git clone git@github.com:guomaoqiu/devopsplatform.git
```
##### 1.安装依赖包
```
yum install -y python-devel python-mysql virtualenv pip supervisor 
pip install -r requirements.txt

#创建虚拟环境并且激活
virtualenv /usr/local/devopsenv
cd /usr/local/devopsenv && source activate
```
##### 2.创建数据库时需要指定编码为UTF8;
```
CREATE DATABASE `DB_NAME` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
grant all on DB_NAME.* to DB_USER@'127.0.0.1' identified by 'PASSWORD';
flush privileges;
```
##### 3.初始化数据库
```
python manager.py db init
python manager.py db migrate
python manager.py db upgrade
```
##### 4.初始化admin管理权限角色数据库
```
#python manage.py shell
from manager import Role
Role.insert_roles()
Role.query.all()
```
##### 5.发布salt grains 获取主机特定或自身的一些属性信息
```
mkdir /srv/salt/_grains/
cp  init/get_server.py  /srv/salt/_grains/
# 同步
salt '*' saltutil.sync_all
# 检查自定义grains是否发布成功
salt '*' grains.items
```
##### 6.Run
```
python manager runserver
```
##### 7.启动后台任务以及周期性任务(-B参数)
```
celery worker -A manager.celery -l info -E -B
```
##### 8.生成supervisor配置
```
ln -sv /usr/local/devopsenv/bin/supervisorctl /usr/bin/
ln -sv /usr/local/devopsenv/bin/supervisord /usr/bin/
/usr/local/devopsenv/bin/echo_supervisord_conf > /etc/supervisor.conf
```
##### 9.添加项目配置到/etc/supervisor.conf
```
[program:devops]
command=/usr/local/devopsenv/bin/gunicorn -w 10  -b 127.0.0.1:5000 manager:app --log-file /tmp/gunicorn.log --log-level=debug
directory=/usr/local/devopsplatform
stopwaitsecs=0
autostart=true
autorestart=true
stdout_logfile=/var/log/gunicorn.log
stderr_logfile=/var/log/gunicorn.error

[program:celery]
command=/usr/local/devopsenv/bin/celery worker -A  manager.celery -l debug 
directory=/usr/local/devopsplatform
stdout_logfile=/var/log/supervisor/celeryd_out.log
stderr_logfile=/var/log/supervisor/celeryd_err.log 
stdout_logfile_maxbytes=20MB 
stdout_logfile_backups=20 
autostart=true 
autorestart=true
startsecs=10
```
##### 10. 通过supervisor来控制
```
supervisord -c /etc/supervisor.conf
supervisorctl -c /etc/supvisrod.conf status all
```
##### 11. nginx 配置(虚拟主机)
```
server {
    listen 80;
    server_name localhost;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    access_log /var/log/devopsplatform_access.log;
    error_log /var/log/devopsplatform_error.log;

}
```


### 平台截图
####  登录界面
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/login_page.jpeg)
#### 用户管理
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/user_manager.jpeg)
#### 访问控制
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/access_con.jpeg)
#### API管理
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/api_test.jpeg)
#### salt客户端管理
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/salt_minion.jpeg)
#### salt命令执行(single host)
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/salt_cmd_host.jpeg)
#### salt命令执行(multi host)
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/salt_cmd_all.jpeg)
#### salt命令执行日志
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/cmd_log.jpeg)
#### zabbix主机批量添加
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/zabbix_add.jpeg)
#### zabbix主机批量删除
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/zabbix_del.jpeg)
#### 主机列表详情页
![](https://raw.githubusercontent.com/guomaoqiu/devopsplatform/master/screenshots/host_detail.jpeg)
