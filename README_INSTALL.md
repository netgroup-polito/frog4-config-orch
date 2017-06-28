## Install Dependencies
; install dependencies
		$ sudo apt-get update
		$ sudo apt-get install python3-setuptools python3-dev python3-pip
		$ sudo pip3 install gunicorn flask flask-restplus

## Install the DoubleDecker client
The frog4-orchestrator uses the [DoubleDecker](https://github.com/Acreo/DoubleDecker-py) messaging system to communicate with the domain orchestrators. Then, you need to install the DoubleDecker client.

		$ git clone https://github.com/Acreo/DoubleDecker-py.git
		$ cd DoubleDecker-py
		$ git reset --hard dc556c7eb30e4c90a66e2e00a70dfb8833b2a652
		$ cp -r [frog4-config-orch]/patches .
		$ git am patches/doubledecker_client_python/0001-version-protocol-rollbacked-to-v3.patch

Now you can install the DoubleDecker as follows:

		; install dependencies
		$ sudo apt-get update
		$ sudo apt-get install python3-setuptools python3-nacl python3-zmq python3-urwid python3-tornado
		; install the doubledecker module and scripts
		$ sudo python3 setup.py install
