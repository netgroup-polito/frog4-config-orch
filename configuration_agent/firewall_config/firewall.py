'''
Created on Dec 26, 2015

@author: fabiomignini
'''

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
from configuration_agent.firewall_config import constants

from configuration_agent import utils
from configuration_agent.utils import Bash
from configuration_agent.common.interface import Interface
        
class Firewall(object):
    '''
    Class that configure and export
    the status of a iptables firewall VNF
    '''
    
    yang_module_name = 'config-firewall'
    type = 'firewall'
    
    def __init__(self):
        self.interfaces = []
        self.json_instance = {self.yang_module_name+':'+'interfaces':{'ifEntry':[]}, 
                              self.yang_module_name+':'+'firewall':{'policy':[]}}

        self.if_entries = self.json_instance[self.yang_module_name+':'+'interfaces']['ifEntry']
        self.yang_model = self.get_yang()
        self.mac_address = utils.get_mac_address(constants.configuration_interface)
    
    def get_json_instance(self):
        '''
        Get the json representing the status
        of the VNF.
        '''
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
        self.get_interfaces_dict()
        self.get_firewall_configuration()
        logging.debug(json.dumps(self.json_instance))
        return self.json_instance
    
    def get_interfaces_dict(self):
        '''
        Get a python dictionary with the interfaces
        of the VNF
        '''
        old_if_entries = self.if_entries
        self.json_instance[self.yang_module_name+':'+'interfaces']['ifEntry'] = []
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
            dict['type'] = interface.type,
        else:
            dict['type'] = 'not_defined'
        if interface.ipv4_address is not None:   
            dict['address'] = interface.ipv4_address
        return dict
    
    def set_status(self, json_instance):
        '''
        Set the status of the VNF starting from a
        json instance
        '''
        logging.debug(json_instance)
        if_entries = json_instance[self.yang_module_name+':'+'interfaces']['ifEntry']
        interfaces = []
        for interface in if_entries:
            # Set interface
            logging.debug(interface)
            new_interface = Interface(name = interface['name'], 
                                        ipv4_address= interface['address'],
                                        _type = interface['type'],
                                        configuration_type= interface['configurationType'])
            new_interface.set_interface()
            interfaces.append(new_interface)
        self.if_entries = if_entries
        self.json_instance = json_instance
        self.if_entries = self.json_instance[self.yang_module_name+':'+'interfaces']['ifEntry']
        
        self.get_interfaces()
        self.get_interfaces_dict()
        logging.debug(self.json_instance)
        self.configure_firewall(self.json_instance[self.yang_module_name+':'+'firewall']['policy']) 
    
    def get_interfaces(self):
        '''
        Retrieve the interfaces of the VM
        '''
        interfaces = netifaces.interfaces()
        self.interfaces = []
        for interface in interfaces:
            if interface == 'lo':
                continue
            interface_af_link_info = netifaces.ifaddresses(interface)[17]
            interface_af_inet_info = netifaces.ifaddresses(interface)[2]
            self.interfaces.append(Interface(name = interface, status = None, 
                      mac_address = interface_af_link_info[0]['addr'],
                      ipv4_address = interface_af_inet_info[0]['addr'],
                      netmask = interface_af_inet_info[0]['netmask'])) 
            
    def get_firewall_configuration(self):
        self.json_instance[self.yang_module_name+':'+'firewall']['policy'] = self.get_iptables_rules()
    
    def get_iptables_rules(self):
        policies = []
        table = iptc.Table(iptc.Table.FILTER)
        for chain in table.chains:
            for rule in chain.rules:
                policy = {}
                if rule.in_interface is not None:
                    policy['in-interface'] = rule.in_interface
                if rule.out_interface is not None:
                    policy['out-interface'] = rule.out_interface
                if rule.protocol is not None:
                    policy['protocol'] = rule.protocol
                else:
                    policy['protocol'] = 'not_defined'
                if rule.src is not None:
                    policy['source-address'] = rule.src.split('/')[0]
                    policy['source-mask'] = rule.src.split('/')[1]
                if rule.dst is not None:
                    policy['destination-address'] = rule.dst.split('/')[0]
                    policy['destination-mask'] = rule.dst.split('/')[1]

                for match in rule.matches:
                    if match.dport is not None:
                        policy['destination-port'] = match.dport
                    if match.sport is not None:
                        policy['source-port'] = match.sport
                policy['action'] = rule.target.name
                policies.append(policy)
        return policies    
                
    def configure_firewall(self, policies):
        # Delete and flush iptables
        Bash('iptables --flush')
        
        chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
        for policy in policies:
            rule = iptc.Rule()
            if 'in-interface' in policy: 
                rule.in_interface = policy['in-interface']
            if 'out-interface' in policy: 
                rule.out_interface = policy['out-interface']
            if 'protocol' in policy:
                rule.protocol = policy['protocol']
                match = rule.create_match(policy['protocol'])
                if 'destination-port' in policy:
                    match.dport =  str(policy['destination-port'])
                if 'source-port' in policy:
                    match.sport =  str(policy['source-port'])
            if 'source-address' in policy:
                rule.src = policy['source-address']+'/'+policy['source-mask']
            if 'destination-address' in policy:
                rule.dst = policy['destination-address']+'/'+policy['destination-mask']
            
            
            
            
            rule.create_target(policy['action'].upper())
            chain.insert_rule(rule)
            
            
        
        """
        Example of policy installed:
        
        iptables -I FORWARD -m physdev --physdev-in eth0 --physdev-out eth1 -d 10.0.0.1 -j DROP
        """
        
    def base_conf(self):
        Bash('echo "UseDNS no" >> /etc/ssh/sshd_config')