#NFV dynamic configuration
This project aims to provide orchestrators a VNFs (Virtual Network Function) dynamic configuration service.
In order to deploy such a service, an orchestrator has to introduce the following components in its own architecture:
* Double Decker bus
* A configuration agent per VNF
* A configuration service
* A configuration repository
![Architecture](https://raw.githubusercontent.com/netgroup-polito/generic-nfv-configuration-and-management/master/images/architecture.jpg)
