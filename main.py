import logging
from threading import Thread

from flask import Flask, request

from config_orch_core.config import Configuration
from config_orch_core.controller.message_bus_controller import MessageBusController
from config_orch_core.rest_api.resources.config import api as configuration_api
from config_orch_core.rest_api.api import root_blueprint

conf = Configuration()

# set log level
log_format = '%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s %(message)s'
log_date_format = '[%d-%m-%Y %H:%M:%S]'

if conf.LOG_LEVEL == "INFO":
    log_level = logging.INFO
elif conf.LOG_LEVEL == "WARNING":
    log_level = logging.WARNING
else:
    log_level = logging.DEBUG

if conf.LOG_FILE is not None:
    logging.basicConfig(filename=conf.LOG_FILE, level=log_level, format=log_format, datefmt=log_date_format)
else:
    logging.basicConfig(level=log_level, format=log_format, datefmt=log_date_format)


# Rest application
logging.info("Rest Server started on: " + conf.REST_ADDRESS + ':' + conf.REST_PORT)
if configuration_api is not None:
    app = Flask(__name__)
    app.register_blueprint(root_blueprint)
    logging.info("Flask Successfully started")

    @app.after_request
    def after_request(response):
        if request.full_path.startswith("/config"):
            logging.debug("'%s' '%s' '%s' '%s' '%s' " % (request.remote_addr, request.method, request.scheme, request.full_path, response.status))
        return response


# start the message bus controller to receive information about network functions
messageBusController = MessageBusController()
thread = Thread(target=messageBusController.start)
thread.start()

logging.debug("FROG4 Configuration Orchestrator started")