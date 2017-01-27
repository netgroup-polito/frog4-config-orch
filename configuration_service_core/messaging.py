from doubledecker import clientSafe
import logging
from threading import Thread
from configuration_service_core import constants
from configuration_service_core.vnf_model import VNF
import sys
import json
from configuration_service_core.my_db import get_default_configuration
from configuration_service_core.log import print_log
from configparser import SafeConfigParser


class MessageBus(clientSafe.ClientSafe):
    _working_thread = None

    def __init__(self):
        print_log('init bus')
        self.parser = SafeConfigParser()
        self.confFile = "config/default-config.ini"
        self.parser.read(self.confFile)
        self.started_vnfs = []
        self.started_vnfs_by_mac_address = {}
        self.started_vnfs_by_id = {}
        self.counter = 0
        self.working_thread = None
        self.vnf_to_configure = {}
        self.initial_registration()
        #self._working_thread.join()

    def registration(self, name, dealerurl, customer, keyfile):
        super().__init__(name=name.encode('utf8'), dealerurl=dealerurl, customer=customer.encode('utf8'), keyfile=keyfile)
        if self._working_thread is None:
            self._working_thread = Thread(target=self.start)
            self._working_thread.start()

    def initial_registration(self):
        self.registration(name='configuration_server',
                          dealerurl=self.parser.get('message_broker', 'dealer'),
                          customer='public',
                          keyfile=self.parser.get('message_broker', 'keyfile'))

    def subscribe_for_tenant_association_phase(self):
        print_log('trying to subscribe')
        self.subscribe('tenant_association', 'noscope')
        print_log('subscribed to: tenant_association')

    def subscribe_for_default_configuration_phase(self):
        self.subscribe('default_configuration', 'noscope')

    def subscribe_vnf_configuration(self):
        self.subscribe('nat', 'noscope')
        self.subscribe('firewall', 'noscope')
        self.subscribe('dhcp', 'noscope')

    def subscribe_status_exportation(self):
        self.subscribe('status_exportation', 'noscope')
        print_log('subscribed to: status exportation')

    def config(self, name, dealerURL, customer):
        super().config(name, dealerURL, customer)

    def on_data(self, dest, msg):
        print_log(msg)

    def on_discon(self):
        print_log("on_discon")
        super().on_discon()

    def on_pub(self, src, topic, msg):
        # msg = msg[0]
        src = src.decode()
        topic = topic.decode()
        msg = msg.decode()
        print_log("on_pub")
        print_log(src)
        print_log(topic)
        print_log(msg)
        if topic =='public.vnf_registration':
            tenant = src.split('.')[0]
            print_log("tenant: " + tenant)

        if topic == 'public.tenant_association':
            # Retrieve tenant id from the mac_address of the VM
            vnf = VNF(mac_address=src)
            print_log("mac=" + src)
            vnf.get_detailed_info()
            self.sendmsg(src, vnf.tenant_id + ',' + vnf.name)

            # Add this VM in the started-up
            self.started_vnfs.append(vnf)
            self.started_vnfs_by_mac_address[vnf.mac_address] = vnf
            self.started_vnfs_by_id[vnf.id] = vnf
        elif topic == 'public.default_configuration':
            print_log('default configuration request received')
            vnf = self.started_vnfs_by_mac_address[src]
            if src in self.vnf_to_configure:
                print_log('src:' + src)
                vnf = self.vnf_to_configure[src]
                print_log(
                    'publishing an old configuration for ' + src + ": " + json.dumps(vnf.configuration_to_push))
                self.sendmsg(vnf.mac_address, json.dumps(vnf.configuration_to_push))
            else:
                print_log('publishing a default configuration for: ' + src)
                configuration_json = get_default_configuration(vnf.id)
                self.sendmsg(vnf.mac_address, configuration_json)
        elif topic == 'public.status_exportation':
            # Configuration publication
            self.started_vnfs_by_mac_address[src].status = msg
            print_log("Configuration json status: " + self.started_vnfs_by_mac_address[src].status + ' of vm: ' +
                         self.started_vnfs_by_mac_address[src].name)

    def on_reg(self):
        '''
        Callback of the registration to the bus
        '''
        print_log('registred')
        # Subscribe to the tenant association phase
        self.subscribe_for_tenant_association_phase()
        # Subscribe to the default configuration phase
        self.subscribe_for_default_configuration_phase()
        # Subscribe to the VNF configuration
        self.subscribe_vnf_configuration()
        # Subscribe to status exportation
        self.subscribe_status_exportation()

    def unsubscribe(self):
        print_log("unsubscribe")
        super().unsubscribe()
        sys.exit(0)

    def signal_handler(self, signal, frame):
        print_log("stop")
        self.shutdown()
        sys.exit(0)

    def on_error(self):
        pass


def message_bus_singleton_factory(_singleton=MessageBus()):
    return _singleton
