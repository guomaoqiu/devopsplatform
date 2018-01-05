#!/data/study/github-file/virtualbox-pystudy/bin/python
#-*- coding:utf8 -*-
# 在3.0版本中host.exists方法已经去除，所以这里判断主机是否存在的方式是获取所有主机的hostname
# 再进行判断.

import sys,time,json
from pyzabbix import ZabbixAPI

class Zabbix():
  # import sys
  # reload(sys)
  # sys.setdefaultencoding( "utf-8" )
  # 获取导入的xls文件名
  file_name = file
  time1 = time.time()
  host_name_list=[]
  host_id_list=[]

######################################################
  def __init__(self,url,user,password):
      self.__url = url
      self.__user = user
      self.__password = password
#####################################################
  def login(self):
      try:
          self.zapi = ZabbixAPI(self.__url)
          self.zapi.login(self.__user,self.__password)
          #print "【登录ZabbixApi接口成功】\n "
      except:
          #print "\n【登录zabbix平台出现错误】"
          sys.exit()

# ####################################################
# 获取所有现在已添加的host及id

  def get_host(self):
      for i in self.zapi.host.get():
          print  i
          self.host_name_list.append(str(i['name']))
          self.host_id_list.append(str(i['hostid']))
      all_host = dict(zip(self.host_name_list, self.host_id_list))

      return all_host.values()
      # for i in all_host.values():
      #     print i

# 获取指定主机的id，通过传入主机名
  def get_each_host(self,hostname):
      data = {
          "output": "extend",
          "filter" : {"name": hostname }
      }
      print hostname
      for i in self.zapi.host.get(**data):
        return i['hostid']

# ####################################################
# 获取所需主机的itemid
  def item_get(self, hostids):
      data = {
          "output": ["itemids","key_"],
          "hostids": hostids,
           "search": {"key_": "system.cpu.load"}
      }
      res = self.zapi.item.get(**data)
      return res
      # for i in ret:
      #     print  i


# ####################################################
# 获取某主机某item的历史数
  def history_get(self, itemid, i, limit=1):
      data = {
              # "output": "extend",
              "history": i,
              "itemids": itemid,
              # "sortfield": "clock",
              "sortorder": "DESC",
              "limit": limit
              }
      ret = self.zapi.history.get(**data)
      return  ret



  def get_graph(self, hostid, ):
      data = {
          "output": "extend",
          "hostids":  hostid,
          "sortfield": "name",
          # "search": v
      }
      print
      ret = self.zapi.graph.get(**data)
      return ret



################ RUN ####################
zclient=Zabbix('http://114.55.0.47:9986','Admin','ZTNiMGM0')
zclient.login()  # 登录Zabbix Api
#for i in zlogin.get_host():

Network = "Network traffic on eth0"

# for i in  zlogin.get_graph(zlogin.get_each_host('shipgs-2-23'),{u"name":u"Network traffic on eth0"}):

for i in  zclient.get_graph(zclient.get_each_host('shipgs-2-23')):
    print i






