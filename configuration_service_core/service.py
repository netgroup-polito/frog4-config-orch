'''
Created on Dec 30, 2015

@author: fabiomignini, DavideXX92

'''
#!/usr/bin/python3
# -*- coding: utf-8 -*-

from configuration_service_core.vnf_model import VNF
import json
import requests
from vnf_template_library.validator import ValidateTemplate
from vnf_template_library.template import Template
from vnf_template_library.exception import TemplateValidationError
from configuration_service_core.log import print_log
from configuration_service_core.messaging import message_bus_singleton_factory
from configparser import SafeConfigParser
from configuration_service_core.pending_configuration import configuration_manager_singleton_factory

config_file = "config/default-config.ini"
parser = SafeConfigParser()
parser.read(config_file)
un_address = parser.get('orchestrator', 'address')
un_port = parser.get('orchestrator', 'port')
un_protocol = "http"
datastore_address = parser.get('datastore', 'address')
datastore_port = parser.get('datastore', 'port')
datastore_protocol = "http"


def get_yang_from_vnf_id(vnf_id):
    '''
        In order to retrieve the YANG model of a VNF you have to:
            a) ask to the UN what is the VNF template uri
            b) retrieve the template from the repository
            b) read the YANG model uri from the VNF template
            c) retrieve the YANG model from the YANG repository
        :param vnf_id:
        :return:
    '''
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    ''' TODO: test as soon as we have the knowledge of the graph id -> data migration on DB
    request_uri = un_protocol + '://' + un_address + ':' + un_port + '/' + 'template/' + graph_id + '/' + vnf_id + '/'
    response = requests.get(request_uri, headers=headers)
    if response.status_code != 200:
        print_log("template not found")
        return ""
    template_path = json.load(response.content)['templateUrl']
    template_uri = datastore_protocol + '://' + datastore_address + ':' + datastore_port + '/v2/nf_template' + template_path + '/'
    '''
    template_uri = "http://130.192.225.193:8081/v2/nf_template/provaDhcp/"

    response_template = requests.get(template_uri, headers=headers)
    print_log("template requested: " + response_template.text)
    template = Template()
    try:
        validator = ValidateTemplate()
        print_log(response_template.text)
        validator.validate(json.loads(response_template.text))
        template.parseDict(response_template.json())
    except TemplateValidationError as e:
        print_log("Error: " + e.message)
        return ""

    yang_model_uri = template.uri_yang
    response_yang = requests.get(yang_model_uri)
    return response_yang.text
'''
When the configuration service receive such a request, it provides the VNF status by both MAC and user ID
'''


def get_status_vnf(mac_vnf, user_id, graph_id):
    '''
    Method called by the dashboard to retrieve the status of a VNF
    '''
    print_log('retrieve status vnf')
    bus = message_bus_singleton_factory()
    mac = 'a.' + mac_vnf
    if mac in bus.started_vnfs_by_mac_address:
        vnf = bus.started_vnfs_by_mac_address[mac]
    else:
        return ""
    if vnf.status is not None:
        print_log("vnf name: " + vnf.name)
        print_log("vnf status: " + vnf.status)
        return vnf.status
    else:
        return ""


def configure_vnf(configuration, mac_vnf, user_id, graph_id):
    if mac_vnf is not None and user_id is not None:
        print_log('MAC VNF: ')
        bus = message_bus_singleton_factory()
        print_log('Message bus retrieved')
        for x in bus.started_vnfs_by_mac_address:
            print_log(x)

        mac = 'a.' + mac_vnf  # The information stored into started_vnfs_by_mac_address is tenant_id.mac_vnf
        if mac in bus.started_vnfs_by_mac_address:
            vnf = bus.started_vnfs_by_mac_address[mac]
        else:
            if mac not in bus.vnf_to_configure:
                vnf = VNF()
                vnf.mac_address = mac
                vnf.configuration_to_push = json.loads(configuration)
                bus.vnf_to_configure[mac] = vnf
                print_log('configuration request for ' + mac + ' saved:\n' + str(vnf.configuration_to_push))
                return True
            else:
                bus.vnf_to_configure[mac].configuration_to_push = json.loads(configuration)
                return True

        configuration_json = json.loads(configuration)
        yang = get_yang_from_vnf_id(mac_vnf)
        print_log('yang retrieved: ' + yang)
        configuration_manager_singleton_factory().configuration_syn(vnf.mac_address, "graph_id", "tenant_id", configuration_json)
        bus.sendmsg(vnf.mac_address, json.dumps(configuration_json))
        return True


def get_vnf_agent_state(vnf_id, graph_id, tenant_id):
    '''
    :param vnf_id:
    :param graph_id:
    :param tenant_id:
    :return: True if the VNf is up, False otherwise
    '''
    keys = message_bus_singleton_factory().started_vnfs_by_mac_address.keys()
    for key in keys:
        if key.split('.')[1] == vnf_id:
            return True
    return False
