'''
Created on Dec 29, 2015

@author: fabiomignini
'''
import requests
import json
import hashlib
import logging
import six

from configuration_server import constants

class Nova(object):
    '''
    Class used to call the Nova Openstack API
    '''
    novaEndpoint = "http://"+constants.openstack_ip+":"+constants.nova_port+"/v2/%s"
    getFlavorsDetail = "/flavors/detail"
    getHypervisorsPath="/os-hypervisors"
    getHypervisorsInfoPath="/os-hypervisors/detail"
    getAvailabilityZonesPath="/os-availability-zone/detail"
    getHostAggregateListPath="/os-aggregates"
    addComputeNodeToHostAggregatePath = "/os-aggregates/%s/action"
    attachInterface = "/servers/%s/os-interface"
    addServer = "/servers"
    getServerDetails = "/servers/detail?all_tenants=1"
    timeout = constants.nova_timeout
    
    def getServersDetails(self, token, tenant_id):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'X-Auth-Token': token}
        endpoint = (self.novaEndpoint % tenant_id)+self.getServerDetails
        logging.debug("Get servers detail endpoint: "+endpoint)
        resp = requests.get(endpoint, headers=headers)
        resp.raise_for_status()
        data = json.loads(resp.text)
        logging.debug(data)
        return data

class Keystone(object):
    '''
    Class used to call the Keystone Openstack API
    '''
    tenant_name = constants.tenant_name 
    username = constants.username
    password = constants.password
    keystone_authentication_url = "http://"+constants.openstack_ip+":"+constants.keystone_port+"/v2.0/tokens"
    authenticationData = {'auth':{'tenantName': tenant_name, 'passwordCredentials':{'username': username, 'password': password}}}
    
    def __init__(self):
        self.createToken()
        
    def createToken(self):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        logging.debug("Authentication endpoint: "+self.keystone_authentication_url)
        resp = requests.post(self.keystone_authentication_url, data=json.dumps(self.authenticationData), headers=headers)
        resp.raise_for_status()
        self.tokendata = json.loads(resp.text)
        self.token = self.tokendata['access'][ 'token']['id']
        logging.debug(self.token)
    
    def getTenantID(self):
        return self.tokendata['access']['token']['tenant']['id']
