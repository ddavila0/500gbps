FROM opensciencegrid/software-base:fresh

RUN yum -y install vim && \
    yum -y install osg-ca-certs && \
    yum -y install osg-xrootd-standalone && \
    yum -y install xrootd-client && \
    yum -y install osg-test osg-ca-generator --enablerepo=devops-itb

ADD influxdb.repo /etc/yum.repos.d/influxdb.repo

RUN yum -y install telegraf

ADD image-config.d/* /etc/osg/image-config.d/
