'''
Created on Dec 29, 2015

@author: fabiomignini
'''
import logging
import constants

#from configuration_server.openstack_rest import Keystone, Nova

class VNF(object):
    def __init__(self, _id = None, name = None, tenant_id = None,
                 status = None, mac_address = None):
        self.id = _id
        self.name = name
        self.tenant_id = tenant_id
        self.status = status
        self.mac_address = mac_address
        
    # def get_detailed_info(self):
    #     kestone = Keystone()
    #     servers_details = Nova().getServersDetails(kestone.token, kestone.getTenantID())
    #     for server in servers_details['servers']:
    #         networks = server['addresses']
    #         for network_name, nics in networks.items():
    #             for nic in nics:
    #                 if self.mac_address == nic['OS-EXT-IPS-MAC:mac_addr']:
    #                     self.id = server['id']
    #                     self.name = server['name']
    #                     self.tenant_id = server['tenant_id']
    #                     break

    def get_detailed_info(self):
        if self.mac_address == "a.52:54:00:fc:92:6e":
            logging.debug("dhcp")
            self.id = constants.id_dhcp
            self.name = constants.vnf_name_dhcp
        elif self.mac_address == "a.52:54:00:3e:28:86":
            logging.debug("nat")
            self.id = constants.id_nat
            self.name = constants.vnf_name_nat
        else:
            logging.debug("nessuna corrispondenza con mac")
        self.tenant_id = constants.tenant_id
