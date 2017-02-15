# Configuration Server

## Installation

- Virtual environment
```sh
$ cd [frog4-configuration-service]
$ virtualenv .env
$ source .env/bin/activate
```

- Tools

```sh	
$ sudo apt-get install python3-setuptools python3-pip libffi-dev
$ sudo pip3 install aiozmq zmq xmltodict pyang
$ sudo pip3 install django==1.8.2 djangorestframework django-rest-swagger==0.3.5 django-chunked-upload django-cors-headers wrapt bcrypt 
```

- Only if you are using Ubuntu 14.04
```sh
$ git clone https://github.com/pyca/pynacl
$ cd pynacl
$ sudo git reset --hard cdc1601af000a35111b5d83ec3eff2a8572b9ad4
$ sudo python3.4 setup.py install
```

- Double Decker
```sh
$ git clone https://github.com/Acreo/DoubleDecker-py.git
$ cd DoubleDecker-py
# follow the README in order to install the dependencies (if you are using Ubuntu 14.04 do NOT install python3-nacl)
$ sudo python3 setup.py install
```

## Configuration

- Configuration file location

constants.py

## Start

- Start broker

```sh
$ ddbroker -r tcp://*:5555 -k <path_key>/<broker_key_file> -s 1/2/3
```

- Start Configuration Server

```sh
$ cd [frog4-configuration-service]
$ source .env/bin/activate
$ sudo python3 manage.py runserver
```
