import logging
import json
import os
from configuration_service_core.log import print_log

def get_default_configuration(vnf_id):
    logging.debug("get_default_configuration - id: " + vnf_id)
    if vnf_id == '12':
        return ""
        #return nat_config()
    elif vnf_id == '123':
        return ""
        #return dhcp_config()
    elif vnf_id == '121':
        return ""
        #return fw_config()


def dhcp_config():
    file_path = "../configuration_example/dhcp_config.json"
    if not os.path.exists(file_path):
        return ""
    fp = open(file_path)
    data = json.dumps(json.load(fp))
    logging.debug(data)
    return data


def nat_config():
    file_path = "../configuration_example/nat_config.json"
    if not os.path.exists(file_path):
        return ""
    fp = open(file_path)
    data = json.dumps(json.load(fp))
    logging.debug(data)
    return data

def fw_config():
    file_path = "../configuration_example/fw_config.json"
    if not os.path.exists(file_path):
        return ""
    fp = open(file_path)
    data = json.dumps(json.load(fp))
    logging.debug(data)
    return data

def contains_vnf(vnf_id):

    know_vnf = ['dhcp', 'fw', 'nat']

    if(vnf_id in know_vnf):
        return True
    else:
        return False

def get_initial_configuration_path(vnf_id):

    if(vnf_id == "dhcp"):
        return "initial_configuration/DHCP_initial_configuration.json"
    elif(vnf_id == "fw"):
        return "initial_configuration/FW_initial_configuration.json"
    elif(vnf_id == "nat"):
        return "initial_configuration/NAT_initial_configuration.json"

def get_template_path(vnf_id):

    if(vnf_id == "dhcp"):
        return "template/DHCP_template.json"
    elif(vnf_id == "fw"):
        return "template/FW_template.json"
    elif(vnf_id == "nat"):
        return "template/NAT_template.json"

def get_metadata_path(tenant_id, graph_id, vnf_id, message_broker_dealer):

    filename = "datadisk/metadata_" + tenant_id + '_' + graph_id + '_' + vnf_id

    file = open(filename, "w")
    file.write("tenant-id = " + tenant_id + '\n')
    file.write("graph-id = " + graph_id + '\n')
    file.write("broker-url = " + message_broker_dealer + '\n')
    file.close()


    return filename

def get_tenant_keys_path(tenant_id=None):
    return "datadisk/tenant-keys.json"
