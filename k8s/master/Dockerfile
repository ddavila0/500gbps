FROM centos/python-38-centos7:latest

RUN yum -y install vim && \
    yum -y install osg-test osg-ca-generator --enablerepo=devops-itb && \
    yum -y install xrootd-client

RUN adduser master    
