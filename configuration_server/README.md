# Configuration Server

## Installation

- Enviroment (Tested on ubuntu 14.04.1)

```sh	
$ sudo apt-get install python3-setuptools python3-pip libffi-dev
$ git clone https://github.com/pyca/pynacl
$ cd pynacl
$ sudo python3.4 setup.py install
$ sudo pip3 install aiozmq	
$ sudo pip3 install zmq
$ sudo pip3 install falcon
$ sudo pip3 install gunicorn
```

- Double Decker

```sh
$ git clone https://github.com/Acreo/DoubleDecker-py.git
$ cd double-decker/python
$ sudo python3 setup.py install
```

## Configuration

- Configuration file location

constants.py

## Start

- Start broker

```sh
ddbroker -r tcp://*:5555 -k <path_key>/<broker_key_file> -s 1/2/3
```

- Start Configuration Server

```sh
cd generic-nfv-configuration-and-management
sudo ./start_server.sh
```
