'''
Created on Dec 18, 2015

@author: fabiomignini
'''
from importlib import reload
import logging
#import xmltodict 
try:
    import StringIO
except ImportError:
    from io import StringIO
import json
import types
import collections
import os
import inspect
import netifaces
import iptc


from pyang.__init__ import Context, FileRepository
from pyang.translators.yin import YINPlugin
from pyang import plugin
from configuration_agent.nat_config import constants

from configuration_agent import utils
from configuration_agent.utils import Bash
from configuration_agent.common.interface import Interface
        
class Nat(object):
    '''
    Class that configure and export
    the status of a NAT VNF
    '''
    
    yang_module_name = 'config-nat'
    type = 'nat'
    
    def __init__(self):
        self.interfaces = []
        self.json_instance = {self.yang_module_name+':'+'interfaces':{'ifEntry':[]}}
        self.if_entries = self.json_instance[self.yang_module_name+':'+'interfaces']['ifEntry']
        self.yang_model = self.get_yang()
        self.mac_address = utils.get_mac_address(constants.configuration_interface)
        self.wan_interface = None
    
    def get_json_instance(self):
        '''
        Get the json representing the status
        of the VNF.
        '''
        logging.debug("exported status: "+json.dumps(self.get_status()))
        return json.dumps(self.get_status())
    
    def get_yang(self):
        '''
        Get from file the yang model of this VNF
        '''
        base_path = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

        with open (base_path+"/"+self.yang_module_name+".yang", "r") as yang_model_file:
            return yang_model_file.read()
    
    def get_status(self):
        '''
        Get the status of the VNF
        '''
        self.get_interfaces()
        self.get_nat_configuration()
        self.get_interfaces_dict()
        logging.debug(json.dumps(self.json_instance))
        return self.json_instance
    
    def get_interfaces_dict(self):
        '''
        Get a python dictionary with the interfaces
        of the VNF
        '''
        old_if_entries = self.if_entries
        self.json_instance[self.yang_module_name+':'+'interfaces']['ifEntry']  = []
        self.if_entries = self.json_instance[self.yang_module_name+':'+'interfaces']['ifEntry']
        for interface in self.interfaces:
            interface_dict = self.get_interface_dict(interface)
            for old_if_entry in old_if_entries:
                if interface.name == old_if_entry['name']:
                    interface.configuration_type = old_if_entry['configurationType'] 
                    interface_dict['configurationType'] = old_if_entry['configurationType'] 
            self.if_entries.append(interface_dict)
    
    def get_interface_dict(self, interface):
        dict = {}
        dict['name'] = interface.name
        if interface.configuration_type is not None:   
            dict['configurationType'] = interface.configuration_type
        else:
            dict['configurationType'] = 'not_defined'
        if interface.type is not None:
            dict['type'] = interface.type
        else:
            dict['type'] = 'not_defined'
        if interface.ipv4_address is not None:   
            dict['address'] = interface.ipv4_address
        if interface.default_gw is not None:
            dict['default_gw'] = interface.default_gw
        return dict
    
    def set_status(self, json_instance):
        '''
        Set the status of the VNF starting from a
        json instance
        '''
        logging.debug(json_instance)
        if_entries = json_instance[self.yang_module_name+':'+'interfaces']['ifEntry']
        interfaces = []
        self.wan_interface = None
        for interface in if_entries:
            # Set interface
            logging.debug(interface)
            if interface['default_gw'] == '':
                default_gw = None
            else:
                default_gw = interface['default_gw']
            new_interface = Interface(name = interface['name'], 
                                        ipv4_address= interface['address'],
                                        _type = interface['type'],
                                        configuration_type= interface['configurationType'],
                                        default_gw = default_gw)
            new_interface.set_interface()
            if new_interface.type == 'wan':
                self.wan_interface = new_interface
            interfaces.append(new_interface)
        self.if_entries = if_entries
        self.json_instance = json_instance
        self.if_entries = self.json_instance[self.yang_module_name+':'+'interfaces']['ifEntry']
        if self.wan_interface is not None:
            self.set_nat(self.wan_interface.name)
        else:
            self.clean_nat()
        self.get_interfaces()
        self.get_interfaces_dict()
    
    def get_interfaces(self):
        '''
        Retrieve the interfaces of the VM
        '''
        interfaces = netifaces.interfaces()
        self.interfaces = []
        for interface in interfaces:
            if interface == 'lo':
                continue
            default_gw = ''
            gws = netifaces.gateways()
            logging.debug("GATEWAY: "+str(gws))
            logging.debug("GATEWAY: "+str(gws['default']))
            logging.debug("GATEWAY: "+str(gws['default'][netifaces.AF_INET]))
            for gw in gws[netifaces.AF_INET]:
                if gw[1] == interface:
                    default_gw = gw[0]
            interface_af_link_info = netifaces.ifaddresses(interface)[17]
            if 2 in netifaces.ifaddresses(interface):
                interface_af_inet_info = netifaces.ifaddresses(interface)[2]
                ipv4_address = interface_af_inet_info[0]['addr']
                netmask = interface_af_inet_info[0]['netmask']
            else:
                ipv4_address = ""
                netmask = ""
            self.interfaces.append(Interface(name = interface, status = None, 
                      mac_address = interface_af_link_info[0]['addr'],
                      ipv4_address = ipv4_address,
                      netmask = netmask,
                      default_gw = default_gw))
    
    def get_nat_configuration(self):
        '''
        Check if a Nat is enabled and  which
        is the wan interface.
        '''
        reload(iptc)
        table = iptc.Table(iptc.Table.NAT)
        try:
            wan_interface = table.chains[3].rules[0].out_interface
        except:
            wan_interface = None
            
        for interface in self.interfaces:
            logging.debug("actual if: "+interface.name+" conf: "+constants.configuration_interface)
            if wan_interface is not None and interface.name == wan_interface:
                interface.type = 'wan'
            elif interface.name == constants.configuration_interface:
                interface.type = 'config'
                interface.configuration_type = 'dhcp'
            elif wan_interface is not None:
                interface.type = 'lan'
    
    def clean_nat(self):
        '''
        Flush the tables of iptables.
        '''
        Bash('iptables --flush')
        Bash('iptables --table nat --flush')
        Bash('iptables --delete-chain')
        Bash('iptables --table nat --delete-chain')
        Bash('iptables --flush')
    
    def set_nat(self, wan_interface):
        '''
        Set a rule to performe as a NAT
        in iptables.
        '''
        Bash('cp /etc/sysctl.conf /etc/sysctl.conf.bak')
        Bash('cp '+os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
+'/sysctl.conf /etc/sysctl.conf')
        
        # Delete and flush iptables
        Bash('iptables --flush')
        Bash('iptables --table nat --flush')
        Bash('iptables --delete-chain')
        Bash('iptables --table nat --delete-chain')
        Bash('iptables --flush')

        #chain = iptc.Chain(iptc.Table(iptc.Table.NAT), "POSTROUTING")
        #rule = iptc.Rule()
        #rule.out_interface = wan_interface
        #target = iptc.Target(rule, "MASQUERADE")
        #rule.target = target
        #chain.insert_rule(rule)
        bash = Bash('iptables -t nat -A POSTROUTING -o '+wan_interface+' -j MASQUERADE')
        Bash('service iptables restart')
        
    def base_conf(self):
        Bash('echo "UseDNS no" >> /etc/ssh/sshd_config')
        
logging.basicConfig(level=logging.DEBUG)
