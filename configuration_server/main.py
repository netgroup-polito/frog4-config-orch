'''
Created on Dec 29, 2015

@author: fabiomignini
'''
import falcon
import logging
from threading import Thread


from server import ConfigurationServer


logging.basicConfig(level=logging.DEBUG)
conf_server = ConfigurationServer()
app = falcon.API()
app.add_route('/status/{image_id}', conf_server)
logging.info("Falcon Successfully started")

working_thread = Thread(target=conf_server.start_configuration_server)
working_thread.start()
logging.info("End")
