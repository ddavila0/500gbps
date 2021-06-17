FROM opensciencegrid/software-base:fresh

ADD influxdb.repo /etc/yum.repos.d/influxdb.repo

RUN yum -y install vim && \
    yum -y install osg-xrootd-standalone && \
    yum -y install unzip && \
    yum -y install osg-ca-generator --enablerepo=devops-itb && \
    yum -y install telegraf && \
    curl -L -O https://github.com/microsoft/ethr/releases/latest/download/ethr_linux.zip && \
    unzip ethr_linux.zip -d /home

ADD image-config.d/* /etc/osg/image-config.d/
