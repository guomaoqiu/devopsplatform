# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: dataapi.py
# @Date:   2018-02-07 17:53:34
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-02-08 16:22:14

import json, random, time
from ..models import DataApi
from .. import db




#######################################################
def graphics_1_api():
    '''
    @note: 饼形图
    '''
    r1 = random.randint(0, 9)
    r2 = random.randint(0, 9)
    r3 = random.randint(0, 9)
    data = {
        "legen":["Chrome",'Firefox','IE10'],
        "series":[r1,r2,r3]
    }
    print data
    data=json.dumps(data, indent=4 ,encoding='utf-8')
    return  data
#######################################################

tmp_time = 0   
def graphics_2_api():
    '''
    @note: 单曲线图
    '''
    global tmp_time
    if tmp_time > 0:
        ss = (db.session.query(DataApi).filter(DataApi.create_time > tmp_time/1000).all())
        print "当前时间",time.time()
    else:
        ss = (db.session.query(DataApi).all())
    data = []
    for i in ss:
        name =  int(i.to_json()["name"])
        ctime =  int(time.mktime(time.strptime(str(i.to_json()['create_time']), "%Y-%m-%d %H:%M:%S")))
        print name,ctime
        data.append([name, ctime])

    #print arr
    print data
    if len(data)>0:
        tmp_time = data[-1][0]
        print tmp_time
    return json.dumps(data)

#######################################################    