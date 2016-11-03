#NFV dynamic configuration

This project aims to provide orchestrators a VNFs (Virtual Network Function) dynamic configuration service.
Such a configuration service is the logic core of the architecture, it pushes configurations into VNFs, retrieves and exports VNFs actual configuration states and communicates with a GUI.
The interactions between the configuration service and the agents are performed through a message bus on a management network.

![Architecture](https://raw.githubusercontent.com/netgroup-polito/generic-nfv-configuration-and-management/master/images/architecture.jpg)
#How to start
* Install Doubledecker C message broker (https://github.com/Acreo/DoubleDecker)
* Install Configuration server (https://github.com/netgroup-polito/generic-nfv-configuration-and-management/blob/master/configuration_server/README.md)
* Create NFVs including a configuration agent (here an example of configuration-service compliant docker: https://github.com/netgroup-polito/un-orchestrator/tree/master/use-cases/configuration-service/docker/dhcp)
* Start Doubledecker broker
* Start configuration server
* Start the GUI (https://github.com/netgroup-polito/fg-gui/tree/b2d60ae631c4414c880e96d11d7b1f65184e42a4)
* Deploy the service graph including some configuration-agent compliant NFVs
* Enjoy configuring your service :)
