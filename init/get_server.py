# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: get_server.py
# @Date:   2018-03-01 17:33:51
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2018-03-01 17:34:31


# 获取已使用内存信息
def get_memory():
  grains = {}
  with open('/proc/meminfo') as f:
    total = int(f.readline().split()[1])
    free = int(f.readline().split()[1])
    buffers = int(f.readline().split()[1])
    cache = int(f.readline().split()[1])
    mem_use = total-free-buffers-cache
    grains['used_memory'] = str(mem_use/1024) + "M"
  return grains