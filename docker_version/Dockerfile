FROM alpine
MAINTAINER guomaoqiu<2399447849@qq.com>

EXPOSE 5000
WORKDIR /opt/project/devopsplatform

RUN echo "https://mirror.tuna.tsinghua.edu.cn/alpine/v3.4/main" > /etc/apk/repositories
	

RUN apk add --update \
    bash \
    git \
    python \
    python-dev \
    py-pip \
    mysql-dev \
    build-base \
  && pip install -i https://pypi.douban.com/simple --upgrade pip \
  && rm -rf /var/cache/apk/*
 

RUN cd /opt/project/ && git clone https://github.com/guomaoqiu/devopsplatform.git
RUN pip install --no-cache-dir -i https://pypi.douban.com/simple -r requirements.txt
CMD python manager.py


