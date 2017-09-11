import json
import logging
from threading import Event

from config_orch_core.config import Configuration
from config_orch_core.dd_client import DDclient
from config_orch_core.service.vnf_service import VnfService


class MessageBusController():

    def __init__(self):
        self.dd_name = Configuration().DD_NAME
        self.broker_address = Configuration().BROKER_ADDRESS
        self.dd_keyfile = Configuration().DD_KEYFILE

        self.is_registered_to_bus = False
        self.registered_to_bus = Event()

        self.vnfService = VnfService()
        self.vnfService.clean_db()

        self.ddClient = DDclient(self)

    def start(self):
        self.registered_to_bus.clear()
        self.ddClient.register_to_bus(self.dd_name, self.broker_address, self.dd_keyfile)
        while self.is_registered_to_bus is False:
            self.registered_to_bus.wait()
        logging.info("DoubleDecker Successfully started")
        self.ddClient.subscribe('vnf_hello', 'noscope')


    def publish_on_bus(self, topic, data):
        self.ddClient.publish_topic(topic, json.dumps(data))

    def on_data_callback(self, src, msg):
        pass
        #logging.debug("[MessageBusController] From: " + src + " Msg: " + msg)

    def on_pub_callback(self, src, topic, msg):
        logging.debug("ON_PUB: src: " + src + " topic: " + topic + " msg: " + msg)
        if topic.__eq__('public.vnf_hello'):
            self._handle_vnf_hello(src, msg)

    def on_reg_callback(self):
        self.is_registered_to_bus = True
        self.registered_to_bus.set()

    def _handle_vnf_hello(self, src, msg):

        tenant_id = None
        graph_id = None
        vnf_id = None
        rest_address = None

        lines = msg.split('\n')
        for line in lines:
            args = line.split(' ')
            if args[0] == "tenant-id":
                tenant_id = args[1]
            elif args[0] == "graph-id":
                graph_id = args[1]
            elif args[0] == "vnf-id":
                vnf_id = args[1]
            elif args[0] == "rest-address":
                rest_address = args[1]
            else:
                logging.debug("Warning: [_handle_vnf_registration]: key: " + args[0] + " unknown, discarted")

        dest = src
        try:
            if not self.vnfService.is_vnf_started(tenant_id, graph_id, vnf_id):
                self.vnfService.save_started_vnf(tenant_id, graph_id, vnf_id, rest_address)
            else:
                curr_rest_address = self.vnfService.get_management_address(tenant_id, graph_id, vnf_id)
                if curr_rest_address != rest_address:
                    self.vnfService.replace_management_address(tenant_id, graph_id, vnf_id, curr_rest_address, rest_address)
                    logging.debug("Replaced management address: " + rest_address + " of: " + tenant_id + '.' + graph_id + '.' + vnf_id)
        except IOError as ex:
            logging.debug("exception: " + ex.message)
        finally:
            msg = "REGISTERED" + ":" + tenant_id + "/" + graph_id + "/" + vnf_id
            self.ddClient.send_message(dest, msg)
            logging.debug(tenant_id + '.' + graph_id + '.' + vnf_id + " registered!")