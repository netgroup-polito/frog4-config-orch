'''
Created on Dec 29, 2015

@author: stack
'''
import requests
import logging
import json

from openstack_dashboard.dashboards.project.instances \
    import constants

LOG = logging.getLogger(__name__)

class ConfigurationServer():
    '''
    Class used to call the Configuration Server API
    '''
    timeout = constants.conf_server_timeout
    ip = constants.conf_server_ip
    port = constants.conf_server_port
    base_url = "http://"+str(ip)+":"+str(port)
    
    status = base_url+"/status/%s"
    
    headers = {'Content-Type': 'application/json'}
    
    def get_vnf_status(self, instance_id):
        resp = requests.get(self.status % (instance_id), headers=self.headers, timeout=long(self.timeout))
        resp.raise_for_status()
        LOG.info("YANG model retrieved from the orchestrator for the instance: "+instance_id+" is: "+resp.text)
        return resp.text
    
    def set_vnf_status(self, instance_id, status):
        data = json.dumps(status)
        resp = requests.put(self.status % (instance_id), data=data, headers=self.headers, timeout=long(self.timeout))
        resp.raise_for_status()
        LOG.info("YANG model retrieved from the orchestrator for the instance: "+instance_id+" is: "+json.dumps(status))

class Orchestrator(object):
    '''
    Class used to call the Orchestrator API
    '''
    timeout = constants.orchestrator_timeout
    ip = constants.orchestrator_ip
    port = constants.orchestrator_port
    base_url = "http://"+str(ip)+":"+str(port)
    
    get_yang = base_url+"/yang/%s"
    get_template_path = base_url+"/template/%s"
    headers = {'Content-Type': 'application/json',
                'cache-control': 'no-cache',
                'X-Auth-User': constants.orchestrator_username,
                'X-Auth-Pass': constants.orchestrator_password,
                'X-Auth-Tenant': constants.orchestrator_tenant}
    
    def get_yang_model(self, instance_id):
        resp = requests.get(self.get_yang % (instance_id), headers=self.headers, timeout=long(self.timeout))
        resp.raise_for_status()
        LOG.info("YANG model retrieved from the orchestrator for the instance: "+instance_id+" is: "+resp.text)
        return resp.text
    
    def get_template(self, instance_id):
        LOG.info("instance_id: "+instance_id)
        resp = requests.get(self.get_template_path % (instance_id), headers=self.headers, timeout=long(self.timeout))
        resp.raise_for_status()
        data = json.dumps(resp.text)
        LOG.info("Template retrieved from the orchestrator for the instance: "+instance_id+" is: "+data)
        return data
        
