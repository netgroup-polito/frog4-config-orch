'''
Created on Dec 30, 2015

@author: fabiomignini, DavideXX92

'''
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from doubledecker import clientSafe
import constants
from vnf_model import VNF
from my_db import get_default_configuration
from yang_parser import yang_to_json

from threading import Thread
import sys
import logging
import json
import falcon
import time

class ConfigurationServer(clientSafe.ClientSafe):
    '''
    Class that extend the safe version of the 
    DD (Double Decker) client, in order to provide 
    a way to configure VNFs.
    '''

    def __init__(self):
        self.started_vnfs = []
        self.started_vnfs_by_mac_address = {}
        self.started_vnfs_by_id = {}
        self.counter = 0
        self.working_thread = None
        
    def start_configuration_server(self):
        # Registration to the DD bus
        self.initial_registration()
        self.working_thread.join()
    
    def registration(self, name, dealerurl, customer, keyfile):
        super().__init__(name=name.encode('utf8'), dealerurl=dealerurl, customer=customer.encode('utf8'), keyfile=keyfile)
        self.working_thread = Thread(target=self.start)
        self.working_thread.start()
        
        
    def initial_registration(self):
        self.registration(name = 'configuration_server',
                          dealerurl = constants.dealer,
                          customer='public',
                          keyfile= constants.keyfile)
    
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
        super().on_discon()
        
    def on_pub(self, src, topic, msg):
        #msg = msg[0]
        src = src.decode()
        topic = topic.decode()
        msg = msg.decode()
        logging.debug("on_pub")
        logging.debug(src)
        logging.debug(topic)
        logging.debug(msg)
        if topic == 'public.tenant_association':
            # Retrieve tenant id from the mac_address of the VM
            vnf = VNF(mac_address = src)
            vnf.get_detailed_info()
            self.sendmsg(src, vnf.tenant_id+','+vnf.name)
            
            # Add this VM in the started-up
            self.started_vnfs.append(vnf)
            self.started_vnfs_by_mac_address[vnf.mac_address] = vnf
            self.started_vnfs_by_id[vnf.id] = vnf
        elif topic == 'public.default_configuration':
            logging.debug('default configuration request received')
            vnf = self.started_vnfs_by_mac_address[src]
            configuration_json = get_default_configuration(vnf.id)
            self.sendmsg(vnf.mac_address, configuration_json)
        elif topic == 'public.status_exportation':
            # Configuration publication
            self.started_vnfs_by_mac_address[src].status = msg
            logging.debug("Configuration json status: "+self.started_vnfs_by_mac_address[src].status+' of vm: '+self.started_vnfs_by_mac_address[src].name)
        
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
        #Subscribe to status exportation
        self.subscribe_status_exportation()
        
    def unsubscribe(self):
        super().unsubscribe()
        sys.exit(0)
    
    def start(self):
        logging.basicConfig(level=logging.DEBUG)
        super().start()
   
    def signal_handler(self, signal, frame):
        logging.debug("stop")
        self.shutdown()    
        sys.exit(0)

    def on_get(self, req, resp):
        logging.debug('ciao')
    ################################# 
    #				    #
    #    - Rest communication -	    #
    #				    #   
    #################################
    '''
    There are multiple type of the same kind of request in order to support more orchesrtators
    '''

    #''' 
    #When the configuration service receive such a request, it provides the VNF status by ID 
    #'''
    #def on_get(self, request, response, image_id):
        #'''
        #Method called by the dashboard to retrieve the status of a VNF
        #'''
        #if image_id in self.started_vnfs_by_id:
            #vnf = self.started_vnfs_by_id[image_id]
        #else:
            #response.status = falcon.HTTP_404
            #return
        #logging.debug(response)
        #logging.debug(vnf)
        #logging.debug(vnf.status)
        #if vnf.status is not None:
            #response.body = vnf.status
        #else:
            #response.status = falcon.HTTP_404
    
    #'''
    #When the configuration service receive such a request, it provides the VNF template (YANG) by VNF type
    #'''
    def get_yang(self, request, response, vnf_type):
        '''
        Method called by the dashboard to retrieve the YANG of a VNF
        '''
        logging.debug('retrieve yang')
        if vnf_type == "nat_cfg":
            logging.debug("nat_cfg")
            yang = yang_to_json("../yang_model_example/config-nat.yang")
        elif vnf_type == "dhcp_cfg":
            logging.debug("dhcp_cfg")
            yang = yang_to_json("../yang_model_example/config-dhcp-server.yang")       
        else:
            logging.debug('YANG not found for: ' + vnf_type)
            response.status = falcon.HTTP_404
            return 
        
        logging.debug(yang)
        response.body = yang
        response.status = falcon.HTTP_200
        
    ''' 
    When the configuration service receive such a request, it provides the VNF status by both MAC and user ID 
    '''
    def get_staus_vnf(self, request, response, mac_vnf, user_id):
        '''
        Method called by the dashboard to retrieve the status of a VNF
        '''
        logging.debug('retrieve status vnf')

        mac = 'a.' + mac_vnf
        if mac in self.started_vnfs_by_mac_address:
            vnf = self.started_vnfs_by_mac_address[mac]
        else:
            response.status = falcon.HTTP_404
            return
        logging.debug(response)
        logging.debug(vnf)
        logging.debug(vnf.status)
        if vnf.status is not None:
            response.body = vnf.status
        else:
            response.status = falcon.HTTP_404
 
    def on_get(self, request, response, mac_vnf=None, user_id=None, vnf_type=None):
        if vnf_type != None:
            self.get_yang(request, response, vnf_type)
        elif mac_vnf != None and user_id != None and vnf_type == None:
            self.get_staus_vnf(request,response, mac_vnf, user_id)

    #def on_put(self, request, response, image_id):
        #'''
        #Method called by the dashboard to configure a VNF
        #'''
        #logging.debug('ID VNF: ')
        #for x in self.started_vnfs_by_id:
            #logging.debug(x)

        #if image_id in self.started_vnfs_by_id:
            #vnf = self.started_vnfs_by_id[image_id]
        #else:
            #response.status = falcon.HTTP_404
            #return
        #configuration_json = json.loads(request.stream.read().decode())
        #NON DA SCOMMENTARE#self.sendmsg(vnf.tenant_id+'.'+vnf.mac_address, json.dumps(configuration_json))
        #self.sendmsg(vnf.mac_address, json.dumps(configuration_json))

    def on_put(self, request, response, mac_vnf, user_id):
        '''
        Method called by the dashboard to configure a VNF
        '''
        logging.debug('MAC VNF: ')
        for x in self.started_vnfs_by_mac_address:
            logging.debug(x)

        mac = 'a.'+mac_vnf #The information stored into started_vnfs_by_mac_address is tenant_id.mac_vnf
        if mac in self.started_vnfs_by_mac_address:
            vnf = self.started_vnfs_by_mac_address[mac]
        else:
            response.status = falcon.HTTP_404
            return
        configuration_json = json.loads(request.stream.read().decode())
        #NON DA SCOMMENTARE#self.sendmsg(vnf.tenant_id+'.'+vnf.mac_address, json.dumps(configuration_json))
        self.sendmsg(vnf.mac_address, json.dumps(configuration_json))

    def on_error():
        pass
        
