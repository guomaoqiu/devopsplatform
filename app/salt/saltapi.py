# -*- coding: utf-8 -*-
import json ,requests, sys, os
from flask import current_app
from app.crypto import prpcrypt
from ..models import ApiMg
import time,json,requests
from .. import db
import datetime
requests.packages.urllib3.disable_warnings()

class SaltApi(object):
    """docstring for SaltApi"""
    def __init__(self):
        '''
        @note 获取saltapi连接所需的账户密码及url
        '''
        prpcrypt_key = prpcrypt(current_app.config.get('PRPCRYPTO_KEY'))  # 调用crypto 解密
        api_info = ApiMg.query.filter_by(app_name="saltstackapi").all()

        for each_info in api_info:
            # 连接用户
            self.__user = each_info.to_json()['api_user']
            # 连接密码
            self.__password = prpcrypt_key.decrypt(each_info.to_json()['api_paas'])
            # 连接url
            self.__url = each_info.to_json()["api_url"]
            # 连接ID
            self.__token_id = self.get_saltapi_token()

            print self.__url,self.__user,self.__password,self.__token_id

    # 添加api后测试该api是否连接正常
    def login_test(self):
        parmes={'eauth': 'pam' ,'username':self.__user,'password':self.__password}
        #print self.__url,self.__user,self.__password,self.__token_id
        self.__my_headers = {
            'Accept': 'application/json'
        }
        try:
            # 进行登录请求，请求时超时时间为5s
            self.__url += '/login'
            req = requests.post(self.__url, headers=self.__my_headers,data=parmes, verify=False, timeout=5)
            if req.status_code == 200:
                return True
            else:
                # 状态码非200返回False
                return False
        # 超时/连接信息
        except Exception ,e:
            print e
            return False

    def get_saltapi_token(self):
        '''
        @note: 登录获取saltapi token
        @summary: 在登录之前查询数据库中的token是否过期(此处6个小时为有效期，配置文件中默认为12个小时)；如果过期则需登录获取，反之直接获取数据库中的
        '''
        api_info = ApiMg.query.filter_by(app_name="saltstackapi").first()
        old_api_token = api_info.api_token_res()
        old_token_create_time = int(time.mktime(time.strptime(str(api_info.api_create_time()), '%Y-%m-%d %H:%M:%S')))
        current_time = int(time.time())
        parmes={'eauth': 'pam' ,'username':self.__user,'password':self.__password}
        print current_time - old_token_create_time
        if (current_time - old_token_create_time) > 43200 or old_api_token == None:
            self.__url += '/login'
            self.__my_headers = {
                'Accept': 'application/json'
                }
            try:
                req = requests.post(self.__url, headers=self.__my_headers,data=parmes, verify=False, timeout=5)
                content = json.loads(req.content)
                token = content["return"][0]['token']
                # 更新token至数据库
                try:
                    api_info = ApiMg.query.filter_by(app_name="saltstackapi").first()
                    api_info.api_token = token
                    api_info.create_time = datetime.datetime.now()
                    db.session.commit()
                except Exception,e:
                    db.session.rollback()
                print '超过过期时间，需要更新token & 或 Token 此前为空',token
                return token
            except Exception,e:
                return e
        else:
            print 'token还在有效期内直接从数据库获取',old_api_token
            old_api_token = api_info.api_token_res()
            return old_api_token

    # run salt cmd
    def saltCmd(self, params):
        '''执行salt操作'''
        headers = {
            'Accept': 'application/json',
            'X-Auth-Token':  self.__token_id
        }
        self.__url = self.__url.strip('/login')
        try:
            req = requests.post(self.__url,data=params,headers=headers,verify=False,timeout=5)
            return req.content
        except Exception, e:
            print e
    # 获取所有的key
    def all_key(self):
        '''
        @note: 获取所有的salt-key
        '''
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        headers = {
            'Accept': 'application/json',
            'X-Auth-Token': self.__token_id
        }
        self.__url = self.__url.strip('/login')
        try:
            req = requests.post(self.__url, data=params, headers=headers, verify=False,timeout=3)
            json_data = dict(json.loads(req.content)['return'][0])['data']['return']
            print json_data
            return json_data
        except Exception,e:
            print e
            return e

    def get_allhostname(self, params):
        '''执行salt操作'''
        headers = {
            'Accept': 'application/json',
            'X-Auth-Token':  self.__token_id
        }
        self.__url = self.__url.strip('/login')

        try:
            req = requests.post(self.__url,data=params,headers=headers,verify=False,timeout=5)

            return req.content
        except Exception, e:
            print e
            return e
    #

    #
    #
    # def get_jid_result(self,jid):
    #     '''
    #     @note: 通过传入的jid获取结果
    #     '''
    #     headers = {
    #         'Accept': 'application/json',
    #         'X-Auth-Token': self.__token_id
    #     }
    #     self.__url = self.__url.strip('/login') + '/jobs/' + jid
    #     try:
    #         req = requests.get(self.__url, headers=headers, verify=False,timeout=2)
    #         json_data = req.content
    #
    #         return json_data
    #     except Exception,e:
    #         print e
    #
    def get_minions(self, host):
        '''
    	@note: 收集主机minion信息
    	'''
        headers = {
            'Accept': 'application/json',
            'X-Auth-Token': self.__token_id
        }
        url = self.__url.strip('/login') + ('/minions/%s' % host)

        req = requests.get(url, headers=headers, verify=False,timeout=2)
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
        print info
        return info
