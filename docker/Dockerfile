FROM opensciencegrid/software-base:fresh

RUN yum -y install vim && \
    yum -y install osg-ca-certs && \
    yum -y install osg-xrootd-standalone && \
    yum -y install xrootd-client && \
    yum -y install osg-test osg-ca-generator --enablerepo=devops-itb

RUN cat <<EOF | tee /etc/yum.repos.d/influxdb.repo
    [influxdb]
    name = InfluxDB Repository - RHEL \$releasever
    baseurl = https://repos.influxdata.com/rhel/\$releasever/\$basearch/stable
    enabled = 1
    gpgcheck = 1
    gpgkey = https://repos.influxdata.com/influxdb.key
    EOF 

RUN yum -y install telegraf

ADD image-config.d/* /etc/osg/image-config.d/
