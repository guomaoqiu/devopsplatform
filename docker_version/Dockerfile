FROM python:2.7
EXPOSE 5000
WORKDIR /opt/project/
RUN

RUN cd /opt/project/ && git clone http://192.168.1.105:3000/guomaoqiu/japan_ops_code.git
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r  /opt/project/japan_ops_code/requirements.txt
CMD python manager.py
