import logging
import json
import os

def get_default_configuration(vnf_id):
    logging.debug("get_default_configuration - id: " + vnf_id)
    if vnf_id == '12':
        return nat_config()
    elif vnf_id == '123':
        return dhcp_config()

def dhcp_config():
    file_path = "../configuration_example/dhcp_config.json"
    if(not os.path.exists(file_path)):
        return ""
    fp = open(file_path)
    data = json.dumps(json.load(fp))
    logging.debug(data)
    return data

def nat_config():
    file_path = "../configuration_example/nat_config.json"
    if(not os.path.exists(file_path)):
        return ""
    fp = open(file_path)
    data = json.dumps(json.load(fp))
    logging.debug(data)
    return data
