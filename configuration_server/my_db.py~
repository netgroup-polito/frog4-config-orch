import logging
import json

def get_default_configuration(vnf_id):
	logging.debug("get_default_configuration - id: " + vnf_id)
	if vnf_id == '12':
                return nat_config()
	elif vnf_id == '123':
		return dhcp_config()

def dhcp_config():
	fp = open("../configuration_agent/dhcp_server_config/default_configuration.json")
	data = json.dumps(json.load(fp))
	logging.debug(data)
	return data
def nat_config(): pass
	fp = open("../configuration_agent/nat_config/default_configuration.json")
	data = json.dumps(json.load(fp))
	logging.debug(data)
	return data
