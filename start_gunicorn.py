from subprocess import call

from config_orch_core.config import Configuration

ip = Configuration().REST_ADDRESS
port = Configuration().REST_PORT
address = str(ip) + ':' + str(port)

call("gunicorn -b " + address + " -t 500 main:app", shell=True)