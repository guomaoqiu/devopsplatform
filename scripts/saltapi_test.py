#-*- coding:utf8 -*-
# __auth__: guomaoqi
import requests,json
import time, os
from ConfigParser import ConfigParser

config = ConfigParser()
config.read("/Volumes/data/study/devopsdemo/config.ini")

requests.packages.urllib3.disable_warnings()
class SaltApi():
    def __init__(self):

        self.__user = config.get("saltapi", "SALT_USER")
        self.__password = config.get("saltapi", "SALT_PASSWORD")
        self.__salt_url = config.get("saltapi", "SALT_URL")

        filepath=('/tmp/tokencache.txt')
        if os.path.exists(filepath) is False:
            #os.mknod(filepath)
            self.__token_id = self.salt_login()
            tinfo = str(int(time.time())) + '\n' + self.__token_id
            with open(filepath, 'w') as f:
                f.write(tinfo)
                f.close()
        elif os.stat(filepath).st_size == 0:
            self.__token_id = self.salt_login()
            tinfo = str(int(time.time())) + '\n' + self.__token_id
            with open(filepath, 'w') as f:
                f.write(tinfo)
                f.close()
        elif os.stat(filepath).st_size != 0:
         
            with open(filepath,'r') as f:
                oldtime = f.readlines()[0].strip('\n')
                f.seek(0)
                oldtoken=f.readlines()[1]
                f.close()
            current_time=int(time.time())
            if current_time < int(oldtime) + 43200: # saltapi token有效期默认12小时
                x = time.localtime(float(oldtime))
                print u'上次Token生成时间为: ',time.strftime('%Y-%m-%d %H:%M:%S',x), oldtoken

                self.__token_id = oldtoken
            else:
                self.__token_id = self.salt_login()

                tinfo = str(int(time.time())) + '\n' + self.__token_id

                filepath = ('/tmp/tokencache.txt')
                with open(filepath, 'w') as f:
                    f.write(tinfo)
                f.close()
        else:
            pass
###########################################################
    # 获取 token
    def salt_login(self,):
        parmes={'eauth': 'pam' ,'username':self.__user,'password':self.__password}
        self.__salt_url += '/login'
        self.__my_headers = {
            'Accept': 'application/json'
        }

        requests.packages.urllib3.disable_warnings()
        req = requests.post(self.__salt_url, headers=self.__my_headers,data=parmes, verify=False,timeout=2)
        content=json.loads(req.content)
        token = content["return"][0]['token']
        return token

###########################################################
    # run salt cmd
    def saltCmd(self, params):
        '''执行salt操作'''
        my_headers = {
            'Accept': 'application/json',
            'X-Auth-Token':  self.__token_id
        }
        self.__salt_url = self.__salt_url.strip('/login')
        try:
            req = requests.post(self.__salt_url,data=params,headers=my_headers,verify=False)
            return req.content
        except IOError:
            raise IOError

###########################################################

    # get minon info
    def get_minions(self, host):

        my_headers = {
            'Accept': 'application/json',
            'X-Auth-Token': self.__token_id
        }
        url = self.__salt_url + ('/minions/%s' % host)

        req = requests.get(url, headers=my_headers, verify=False)
        json_data = json.loads(req.content)

        hostname = host.encode('raw_unicode_escape')
        release = json_data['return'][0]["%s" % host]["osfullname"].encode('raw_unicode_escape') + ' ' + json_data['return'][0]["%s" % host]["osrelease"].encode('raw_unicode_escape')
        kernelrelease = json_data['return'][0]["%s" % host]["kernelrelease"].encode('raw_unicode_escape')
        num_cpus = json_data['return'][0]["%s" % host]["num_cpus"]
        cpu_type= json_data['return'][0]["%s" % host]["cpu_model"].encode('raw_unicode_escape')
        mem_total = json_data['return'][0]["%s" % host]["mem_total"]
        private_ip = json_data['return'][0]["%s" % host]["ip4_interfaces"]["eth0"][0].encode('raw_unicode_escape')
        info = {
            'hostname': hostname,
            'os_release': release,
            'mem_total': mem_total,
            'num_cpus': num_cpus,
            'cpu_type':cpu_type,
            'private_ip': private_ip,
            'public_ip': '',
            'kernelrelease': kernelrelease
        }
        return info

    def get_jobs(self,job_num):
        my_headers = {
            'Accept': 'application/x-yaml',
            'X-Auth-Token': self.__token_id
        }
        url = self.__salt_url + ('/jobs/%s' % job_num)

        req = requests.get(url, headers=my_headers, verify=False)
        json_data = json.loads(req.content)
        return json_data
#
if __name__ == "__main__":
    client=SaltApi()

   #对分组执行salt命令
    #params = {'client': 'local', 'fun': 'test.ping', 'tgt': 'gameserver', 'expr_form': 'nodegroup'}

    #执行部署sls文件，需要先编写 sls文件。 默认的是base环境.

    #params = {'client':'local', 'fun':'state.sls', 'tgt':'salt-minion-node1', 'arg':'one'}

    # 查询所有key的信息
    # params = {'client': 'wheel', 'fun': 'key.list_all'}
    # json_data = dict(json.loads(client.saltCmd(params=params))['return'][0])['data']['return']
    # print "未认证的key: " , json_data['minions_denied']
    # for s in json_data['minions']:
    #     print "已认证key: " , s
    #
    # print "已拒绝key: " , json_data['minions_rejected']
    # for s in json_data['minions_pre']:
    #     print "未认证key: " , s

    #jid =
    #params = {'client':'runner', 'fun':'jobs.lookup_jid', 'jid':jid}
    #print client.saltCmd(params=params)
    #res = json.loads(client.saltCmd(params=params))
    #print res
    #print client.saltCmd(params=params)
    #json_data=json.loads(client.saltCmd(params=params))['return']
    #print json_data

    #jid=dict(json.loads(client.saltCmd(params=params))['return'][0]).values()[0]

    #print client.get_jobs(jid)

    #print json_data
#     #params = {'client':'local', 'fun':'test.ping', 'tgt':'gameserver','expr_form':'nodegroup'}
#     print client.saltCmd(params=params)



