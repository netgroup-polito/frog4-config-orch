'''
Created on Dec 28, 2015

@author: fabiomignini
'''
import logging

from configuration_agent.agent import ConfigurationAgent
from configuration_agent.firewall_config.firewall import Firewall

logging.basicConfig(level=logging.DEBUG)
ConfigurationAgent(Firewall())

"""
Firewall configuration instance example:

{
  "config-firewall:interfaces": {
    "ifEntry": [
      {
        "name": "eth0",
        "configurationType": "static",
        "type": "data",
        "address": "192.168.0.1"
      },
      {
        "name": "eth1",
        "configurationType": "static",
        "type": "config",
        "address": "10.0.0.100"
      }
    ]
  },
  "config-firewall:firewall": {
      "policy": [
          {
              "policy-name": "test",
              "action": "drop",
              "interface": "eth0",
              "source-address": "10.0.0.1",
              "destination-address": "10.0.0.1",
              "tcp-source-port": 1000,
              "tcp-destination-port": 2000
          }
      ]
  }
}
"""