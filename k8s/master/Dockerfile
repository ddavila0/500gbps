FROM opensciencegrid/software-base:fresh

RUN yum -y install gcc openssl-devel bzip2-devel libffi-devel && \
    yum -y install vim

CMD curl https://www.python.org/ftp/python/3.8.7/Python-3.8.7.tgz -o /tmp/Python.tgz && \
    tar xzf /tmp/Python.tgz && \
    /bin/sh /tmp/Python-3.8.7/configure --enable-optimizations && \
    cd /tmp/Python-3.8.7 && \
    make altinstall
