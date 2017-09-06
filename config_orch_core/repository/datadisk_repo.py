from config_orch_core.exception.file_not_found import FileNotFound
from config_orch_core.exception.functional_capability_not_found import FunctionalCapabilityNotFound
import os

local_db_path = "local_database"

class DatadiskRepo():

    def get_file_list(self, functional_capability):
        supported_functional_capabilities = ['nat', 'firewall', 'dhcp', 'iperf', 'iperf_client', 'iperf_server', 'traffic_shaper']
        if functional_capability not in supported_functional_capabilities:
            raise FunctionalCapabilityNotFound("Functional capability " + functional_capability + " unsupported")
        else:
            file_list = [
                "tenant-keys.json",
                "template.json",
                "initial_configuration.json",
                "metadata.json"
            ]
            return file_list


    def get_initial_configuration_path(self, tenant_id, graph_id, vnf_id):
        raise FileNotFound("initial_configuration.json not found for: " + tenant_id +'/'+ graph_id +'/'+ vnf_id)

    def get_template_path(self, tenant_id, graph_id, vnf_id):
        raise FileNotFound("templates.json not found for: " + tenant_id + '/' + graph_id + '/' + vnf_id)

    def get_metadata_path(self, tenant_id, graph_id, vnf_id, broker_address):

        filename = local_db_path+"/metadata/metadata_" + tenant_id + '_' + graph_id + '_' + vnf_id + ".json"

        file = open(filename, "w")
        file.write("{")
        file.write('"tenant-id": "' + tenant_id + '",\n')
        file.write('"graph-id": "' + graph_id + '",\n')
        file.write('"vnf-id": "' + vnf_id + '",\n')
        file.write('"broker-url": "tcp://10.0.0.2:5555"')
        #file.write('"broker-url: "' + broker_address)
        file.write("}")

        file.close()

        return filename

    def get_tenant_keys_path(self, tenant_id):
        return local_db_path+"/tenant-keys.json"


    def get_initial_configuration_path_default(self, functional_capability):

        if (functional_capability == "dhcp"):
            return local_db_path+"/initial_configuration/DHCP_initial_configuration.json"

        elif (functional_capability == "firewall"):
            return local_db_path+"/initial_configuration/FW_initial_configuration.json"

        elif (functional_capability == "nat"):
            return local_db_path+"/initial_configuration/NAT_initial_configuration.json"

        elif (functional_capability == "traffic_shaper"):
            return local_db_path+"/initial_configuration/TRAFFIC_SHAPER_initial_configuration.json"

        elif (functional_capability == "iperf"):
            return local_db_path+"/initial_configuration/IPERF_initial_configuration.json"
        elif (functional_capability == "iperf_client"):
            return local_db_path+"/initial_configuration/IPERF_CLIENT_initial_configuration.json"
        elif (functional_capability == "iperf_server"):
            return local_db_path+"/initial_configuration/IPERF_SERVER_initial_configuration.json"

        else:
            raise FunctionalCapabilityNotFound("Functional capability " + functional_capability + " unknown")

    def get_template_path_default(self, functional_capability):

        if (functional_capability == "dhcp"):
            return local_db_path+"/templates/DHCP_template.json"

        elif (functional_capability == "firewall"):
            return local_db_path+"/templates/FW_template.json"

        elif (functional_capability == "nat"):
            return local_db_path+"/templates/NAT_template.json"

        elif (functional_capability == "traffic_shaper"):
            return local_db_path + "/templates/TRAFFIC_SHAPER_template.json"

        elif (functional_capability == "iperf" or functional_capability == "iperf_client" or functional_capability == "iperf_server"):
            return local_db_path + "/templates/IPERF_template.json"

        else:
            raise FunctionalCapabilityNotFound("Functional capability " + functional_capability + " unknown")