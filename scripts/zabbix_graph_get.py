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



  def get_graph(self, hostid, v):
      data = {
          "output": "extend",
          "hostids":  hostid,
          "sortfield": "name",
          "search": v

      }
      ret = self.zapi.graph.get(**data)
      return ret



################ RUN ####################
zlogin=Zabbix('http://114.55.0.47:9986','Admin','ZTNiMGM0')
zlogin.login()  # 登录Zabbix Api
#for i in zlogin.get_host():



for i in  zlogin.get_graph(zlogin.get_each_host('shipgs-2-23'),{u"name":u"Network traffic on eth0"}):
    print i['graphid']

#print zlogin.get_each_host('shipgs-2-23')
#zlogin.get_host()

  # def run(self):
  #     zlogin=Zabbix('http://114.55.0.47:9986','Admin','ZTNiMGM0')
  #     zlogin.login()  # 登录Zabbix Api
  #
  #     v = []
  #     for i in zlogin.item_get('10205'): # 获取主机item ,代码中可以过滤掉特定的key_
  #         for s in zlogin.history_get(dict(i).values(),0):
  #             # print s
  #             v.append(s['value'])
  #
  #             data = {
  #
  #                     "name": [u"15 min",u"1 min",u"5 min"],
  #                     "series":v
  #
  #             }
  #
  #     data=json.dumps(data, indent=4 ,encoding='utf-8')
  #     return data



    #print zlogin.get_host()
    #print zlogin.item_get('10106')
    # for i in  zlogin.item_get('10134'):
    #     for s in zlogin.history_get(dict(i).values(),0):
    #         print s
    # for i in zlogin.get_host():
    #     print '主机 %s 的cpuload ' % i , zlogin.item_get(i)
    # #zlogin.item_get()
    # for i in zlogin.history_get('28411',0):
    #     print i
#











