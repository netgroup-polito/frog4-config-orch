# Configuration Agent

## Installation

- Enviroment (Tested on ubuntu 14.04.1)

```sh
$ sudo apt-get install python3-setuptools python3-pip libffi-dev
$ git clone https://github.com/pyca/pynacl
$ cd pynacl
$ sudo python3.4 setup.py install
$ sudo pip3 install aiozmq	
$ sudo pip3 install zmq
$ sudo pip3 install pyang
$ sudo apt-get install xsltproc
$ sudo apt-get install jing
$ sudo sudo pyp3 install netifaces
$ sudo sudo pyp3 install xmltodict
$ sudo pip3 install --upgrade python-iptables
$ sudo pip3 install netaddr
$ sudo pyp3 install iptools
```

- Double Decker

```sh
$ git clone http://gitlab.testbed.se/monitoring-and-measurements/double-decker.git
$ cd double-decker/python
$ sudo python3 setup.py install
```

## Configuration

- Configuration file location

constants.py # For general variables
/<vnf>_config/constants.py # For VNF specific variables

## Start

- Start Configuration agent

```sh
cd openstack-nfv-configuration-and-management
sudo ./start_<vnf>_agent_in_screen.sh
```


