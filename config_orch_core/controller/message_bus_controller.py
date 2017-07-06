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
        self.ddClient.subscribe('vnf_registration', 'noscope')


    def publish_on_bus(self, topic, data):
        self.ddClient.publish_topic(topic, json.dumps(data))

    def on_data_callback(self, src, msg):
        pass
        #logging.debug("[MessageBusController] From: " + src + " Msg: " + msg)

    def on_pub_callback(self, src, topic, msg):
        logging.debug("ON_PUB: src: " + src + " topic: " + topic + " msg: " + msg)
        if topic.__eq__('public.vnf_registration'):
            self._handle_vnf_registration(src, msg)
        elif topic.split('/')[1].__eq__("restServer"):
            self._handle_reception_of_management_address(topic, msg)


    def on_reg_callback(self):
        self.is_registered_to_bus = True
        self.registered_to_bus.set()

    def _handle_vnf_registration(self, src, msg):

        tenant_id = None
        graph_id = None
        vnf_id = None

        lines = msg.split('\n')
        for line in lines:
            words = line.split(':')
            if words[0] == "tenant-id":
                tenant_id = words[1]
            elif words[0] == "graph-id":
                graph_id = words[1]
            elif words[0] == "vnf-id":
                vnf_id = words[1]
            else:
                logging.debug("Warning: [_handle_vnf_registration]: key: " + words[0] + "unknown, discarted")

        dest = src
        try:
            if not self.vnfService.is_vnf_started(tenant_id, graph_id, vnf_id):
                self.vnfService.save_started_vnf(tenant_id, graph_id, vnf_id)
                self.ddClient.subscribe(tenant_id+'.'+graph_id+'.'+vnf_id+"/restServer", 'noscope')
        except IOError as ex:
            logging.debug("Error, unable to save started vnf.")
            logging.debug("exception: " + ex.message)
        finally:
            self.ddClient.send_message(dest, "REGISTERED")
            logging.debug(tenant_id + '.' + graph_id + '.' + vnf_id + " registered!")

    def _handle_reception_of_management_address(self, topic, msg):
        triple = topic.split('/')[0]
        values = triple.split('.')
        # values[0]=public
        tenant_id = values[1]
        graph_id = values[2]
        vnf_id = values[3]
        try:
            if self.vnfService.is_vnf_started(tenant_id, graph_id, vnf_id):
                address = self.vnfService.get_management_address(tenant_id, graph_id, vnf_id)
                if address is None:
                    self.vnfService.save_management_address(tenant_id, graph_id, vnf_id, msg)
                    logging.debug("Saved management address: " + msg + " of: " + tenant_id+'.'+graph_id+'.'+vnf_id )
            else:
                logging.error("Received a management address from a vnf not known:")
                logging.error("Address: " + topic[1] + " From: tenant_id: " + tenant_id + ", graph_id: " + graph_id + ", vnf_id: " + vnf_id)
        except IOError as err:
            logging.error(err)