FROM opensciencegrid/software-base:fresh

RUN yum -y install vim && \
    yum -y install osg-xrootd-standalone && \
    yum -y install unzip && \
    yum -y install osg-test osg-ca-generator --enablerepo=devops-itb

RUN curl -L -O https://github.com/microsoft/ethr/releases/latest/download/ethr_linux.zip && \
    unzip ethr_linux.zip -d /home

ADD influxdb.repo /etc/yum.repos.d/influxdb.repo

RUN yum -y install telegraf

ADD image-config.d/* /etc/osg/image-config.d/
