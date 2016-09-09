'''
Created on Dec 29, 2015
@author: fabiomignini
'''
dealer = 'tcp://localhost:5555'
openstack_ip = 'controller.ipv6.polito.it'
nova_port = '8774'
keystone_port = '35357'
# Timeout in seconds
nova_timeout = '10'
tenant_name = 'admin'
username = 'admin'
password = 'SDN@Edge_Polito'

keyfile = '/etc/doubledecker/public-keys.json'

#parametri statici aggiunti da get_detailed_info di vnf_model
tenant_id = '123'

id_dhcp = '123'
vnf_name_dhcp = 'dhcp'

id_nat = '12'
vnf_name_nat = 'nat'
