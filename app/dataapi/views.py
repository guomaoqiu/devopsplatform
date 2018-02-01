# -*- coding:utf-8 -*-
from flask_login import login_required
from . import dataapi
import json
from .. import db

@dataapi.route('/query3',methods=['GET','POST'])
@login_required
def query3():
    import random
    r1 = random.randint(0, 9)
    r2 = random.randint(0, 9)
    r3 = random.randint(0, 9)
    data = {
        "legen":["Chrome",'Firefox','IE10'],
        "series":[r1,r2,r3]
    }
    data=json.dumps(data, indent=4 ,encoding='utf-8')
    return  data
