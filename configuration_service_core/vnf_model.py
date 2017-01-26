'''
Created on Dec 29, 2015

@author: fabiomignini
'''
import logging
from configuration_service_core import constants


class VNF(object):
    def __init__(self, _id = None, name = None, tenant_id = None,
                 status = None, mac_address = None):
        self.id = _id
        self.name = name
        self.tenant_id = tenant_id
        self.status = status
        self.mac_address = mac_address

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

