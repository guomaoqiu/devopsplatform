#-*- coding:utf8 -*-
#-*- coding:utf8 -*-
import requests,json,sys
import time, os
from ConfigParser import ConfigParser
config = ConfigParser()
config.read("config.ini")
from app import config


# 禁用警告
requests.packages.urllib3.disable_warnings()
class SaltApi():
    def __init__(self):
        self.__user = config.get("saltapi", "SALT_USER")
        self.__password = config.get("saltapi", "SALT_PASSWORD")
        self.__salt_url = config.get("saltapi", "SALT_URL")
        

###########################################################
    # 获取 token
    def salt_login(self,):
        print self.__user
        parmes={'eauth': 'pam' ,'username':self.__user,'password':self.__password}
        self.__salt_url += '/login'
        self.__my_headers = {
            'Accept': 'application/json'
        }
        try:
            print u'【登陆成功】'
            req = requests.post(self.__salt_url, headers=self.__my_headers,data=parmes, verify=False)
            content=json.loads(req.content)
            token = content["return"][0]['token']
            print  token
        except:
            print u'登录失败'
      #  print 'newtoken: ',token



