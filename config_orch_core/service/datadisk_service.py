from config_orch_core.config import Configuration
from config_orch_core.repository.datadisk_repo import DatadiskRepo
from config_orch_core.exception.file_not_found import FileNotFound
from config_orch_core.exception.functional_capability_not_found import FunctionalCapabilityNotFound

class DatadiskService():

    def __init__(self):
        self.datadiskRepo = DatadiskRepo()

    def get_file_list(self, functional_capability):
        try:
            return self.datadiskRepo.get_file_list(functional_capability)

        except FunctionalCapabilityNotFound as err:
            raise err

    def get_file(self, tenant_id, graph_id, vnf_id, filename):
        try:

            if(filename.__eq__("tenant-keys.json")):
                return self.datadiskRepo.get_tenant_keys_path(tenant_id)

            elif (filename.__eq__("template.json")):
                return self.datadiskRepo.get_template_path(tenant_id, graph_id, vnf_id)

            elif (filename.__eq__("initial_configuration.json")):
                return self.datadiskRepo.get_initial_configuration_path(tenant_id, graph_id, vnf_id)

            elif (filename.__eq__("metadata.json")):
                return self.datadiskRepo.get_metadata_path(tenant_id, graph_id, vnf_id, Configuration().BROKER_ADDRESS)

            else:
                raise FileNotFound("File: " + filename + " not found")

        except FileNotFound as err:
            raise err

    def get_file_default(self, functional_capability, filename):
        try:

            if (filename.__eq__("template.json")):
                return self.datadiskRepo.get_template_path_default(functional_capability)

            elif (filename.__eq__("initial_configuration.json")):
                return self.datadiskRepo.get_initial_configuration_path_default(functional_capability)

            else:
                raise FileNotFound("File: " + filename + " not found")

        except FunctionalCapabilityNotFound as err:
            raise err