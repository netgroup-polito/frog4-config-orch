FROM      ubuntu
MAINTAINER Politecnico di Torino

RUN apt-get update && apt-get install -y iptables

RUN apt-get install -y python3-setuptools python3-pip libffi-dev
RUN apt-get install -y git
RUN apt-get install -y net-tools
RUN apt-get install -y sudo
RUN git clone https://github.com/pyca/pynacl.git
RUN cd pynacl && ls && python3 setup.py install
RUN pip3 install aiozmq  
RUN pip3 install zmq
RUN pip3 install pyang
RUN apt-get install -y xsltproc
RUN apt-get install -y jing
RUN pip3 install netifaces
RUN pip3 install xmltodict
RUN pip3 install --upgrade python-iptables
RUN pip3 install netaddr
RUN pip3 install iptools

RUN pip3 install PyNaCl
RUN pip3 install pyzmq
RUN pip3 install tornado
RUN pip3 install cffi
RUN pip3 install urwid

RUN git clone https://github.com/Acreo/DoubleDecker-py.git
WORKDIR DoubleDecker-py
RUN python3 setup.py install

RUN mkdir /etc/doubledecker
ADD a-keys.json /etc/doubledecker/a-keys.json
ADD b-keys.json /etc/doubledecker/b-keys.json
ADD public-keys.json /etc/doubledecker/public-keys.json

WORKDIR / 
ADD sysctl.conf /etc/sysctl.conf
ADD ./start.sh start.sh

RUN git clone https://github.com/netgroup-polito/generic-nfv-configuration-and-management.git

RUN apt-get -y install iputils-ping

RUN chmod +x start.sh
CMD ./start.sh


WORKDIR /generic-nfv-configuration-and-management
RUN chmod +x ./start_nat_agent.sh
RUN echo "configuration_interface='eth0'" > ./configuration_agent/nat_config/constants.py
RUN echo "# Configuration Agent - configuration file "\
   "dealer = 'tcp://10.0.0.2:5555' "\
   "keyfile = '/etc/doubledecker/a-keys.json' " > ./configuration_agent/constants.py
CMD ./start_nat_agent.sh
