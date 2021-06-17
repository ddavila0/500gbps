FROM opensciencegrid/software-base:fresh

ADD influxdb.repo /etc/yum.repos.d/influxdb.repo

RUN yum -y install vim && \
    yum -y install osg-xrootd-standalone && \
    yum -y install unzip && \
    yum -y install telegraf && \
    curl -O https://kojihub0000.chtc.wisc.edu/kojifiles/packages/osg-ca-generator/1.4.0/1.osg35.el7/noarch/osg-ca-generator-1.4.0-1.osg35.el7.noarch.rpm && \
    yum -y localinstall osg-ca-generator-1.4.0-1.osg35.el7.noarch.rpm
    curl -L -O https://github.com/microsoft/ethr/releases/latest/download/ethr_linux.zip && \
    unzip ethr_linux.zip -d /home

ADD image-config.d/* /etc/osg/image-config.d/
