FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y openssh-server && \
    apt-get install -y iptables && \
    apt-get install -y busybox && \
    apt-get install -y nano && \
    apt-get install -y curl && \
    apt-get install -y netcat && \
    apt-get install -y iputils-ping


RUN mkdir /var/run/sshd && \
    echo 'root:LTFE_cowrie_adahon_123' | chpasswd && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

RUN useradd -ms /bin/bash admin && \
    echo 'admin:Adahon_prod_past_123' | chpasswd

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh 

EXPOSE 22
CMD ["/usr/local/bin/start.sh"]

