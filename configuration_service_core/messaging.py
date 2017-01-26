from doubledecker import clientSafe
import logging
from threading import Thread
from configuration_service_core import constants
from configuration_service_core.vnf_model import VNF
import sys
import json
from configuration_service_core.my_db import get_default_configuration
import time


class MessageBus(clientSafe.ClientSafe):
    _instance = None
    _working_thread = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MessageBus, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        print("sto per registrarmi")
        self.initial_registration()
        self._working_thread.join()
        print("before sleeping")

    def registration(self, name, dealerurl, customer, keyfile):
        super(MessageBus, self).__init__(name=name.encode('utf8'), dealerurl=dealerurl, customer=customer.encode('utf8'), keyfile=keyfile)
        if self._working_thread is None:
            self._working_thread = Thread(target=self.start)
            self._working_thread.start()

    def initial_registration(self):
        self.registration(name='configuration_server',
                          dealerurl=constants.dealer,
                          customer='public',
                          keyfile=constants.keyfile)

    def subscribe_for_tenant_association_phase(self):
        logging.debug('trying to subscribe')
        self.subscribe('tenant_association', 'noscope')
        logging.debug('subscribed to: tenant_association')

    def subscribe_for_default_configuration_phase(self):
        self.subscribe('default_configuration', 'noscope')

    def subscribe_vnf_configuration(self):
        self.subscribe('nat', 'noscope')
        self.subscribe('firewall', 'noscope')
        self.subscribe('dhcp', 'noscope')

    def subscribe_status_exportation(self):
        self.subscribe('status_exportation', 'noscope')
        logging.debug('subscribed to: status exportation')

    def config(self, name, dealerURL, customer):
        super().config(name, dealerURL, customer)

    def on_data(self, dest, msg):
        logging.debug(msg)

    def on_discon(self):
        logging.debug("on_discon")
        super().on_discon()

    def on_pub(self, src, topic, msg):
        # msg = msg[0]
        src = src.decode()
        topic = topic.decode()
        msg = msg.decode()
        logging.debug("on_pub")
        logging.debug(src)
        logging.debug(topic)
        logging.debug(msg)
        if topic == 'public.tenant_association':
            # Retrieve tenant id from the mac_address of the VM
            vnf = VNF(mac_address=src)
            vnf.get_detailed_info()
            self.sendmsg(src, vnf.tenant_id + ',' + vnf.name)

            # Add this VM in the started-up
            self.started_vnfs.append(vnf)
            self.started_vnfs_by_mac_address[vnf.mac_address] = vnf
            self.started_vnfs_by_id[vnf.id] = vnf
        elif topic == 'public.default_configuration':
            logging.debug('default configuration request received')
            vnf = self.started_vnfs_by_mac_address[src]
            if src in self.vnf_to_configure:
                logging.debug('src:' + src)
                vnf = self.vnf_to_configure[src]
                logging.debug(
                    'publishing an old configuration for ' + src + ": " + json.dumps(vnf.configuration_to_push))
                self.sendmsg(vnf.mac_address, json.dumps(vnf.configuration_to_push))
            else:
                logging.debug('publishing a default configuration for: ' + src)
                configuration_json = get_default_configuration(vnf.id)
                self.sendmsg(vnf.mac_address, configuration_json)
        elif topic == 'public.status_exportation':
            # Configuration publication
            self.started_vnfs_by_mac_address[src].status = msg
            logging.debug("Configuration json status: " + self.started_vnfs_by_mac_address[src].status + ' of vm: ' +
                         self.started_vnfs_by_mac_address[src].name)

    def on_reg(self):
        '''
        Callback of the registration to the bus
        '''
        logging.debug('registred')
        # Subscribe to the tenant association phase
        self.subscribe_for_tenant_association_phase()
        # Subscribe to the default configuration phase
        self.subscribe_for_default_configuration_phase()
        # Subscribe to the VNF configuration
        self.subscribe_vnf_configuration()
        # Subscribe to status exportation
        self.subscribe_status_exportation()

    def unsubscribe(self):
        logging.debug("unsubscribe")
        super().unsubscribe()
        sys.exit(0)

    def signal_handler(self, signal, frame):
        logging.debug("stop")
        self.shutdown()
        sys.exit(0)

    def on_error(self):
        pass
