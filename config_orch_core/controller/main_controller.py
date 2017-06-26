from config_orch_core.service.datadisk_service import DatadiskService
from config_orch_core.service.vnf_service import VnfService
from config_orch_core.service.configuration_service import ConfigurationService
from config_orch_core.exception.file_not_found import FileNotFound
from config_orch_core.exception.functional_capability_not_found import FunctionalCapabilityNotFound
from config_orch_core.exception.vnf_not_started import VnfNotStarted
from config_orch_core.exception.management_address_not_found import ManagementAddressNotFound
from requests.exceptions import HTTPError

class MainController():

    def __init__(self):
        self.datadiskService = DatadiskService()
        self.vnfService = VnfService()
        self.configurationService = ConfigurationService()

    def get_started_vnf(self):
        try:
            started_vnf = self.vnfService.get_started_vnf()
        except IOError as err:
            raise err
        started_vnf_dict = []
        for vnf in started_vnf:
            started_vnf_dict.append(vnf.toJson())
        return started_vnf_dict

    def retrieve_file_list(self, functional_capability):
        try:
            return self.datadiskService.get_file_list(functional_capability)
        except FunctionalCapabilityNotFound as err:
            raise err
        except Exception as err:
            raise err

    def retrieve_file(self, tenant_id, graph_id, vnf_id, filename):
        try:
            return self.datadiskService.get_file(tenant_id, graph_id, vnf_id, filename)
        except FileNotFound as err:
            raise err
        except Exception as err:
            raise err

    def retrieve_file_default(self, functional_capability, filename):
        try:
            return self.datadiskService.get_file_default(functional_capability, filename)
        except FunctionalCapabilityNotFound as err:
            raise err
        except FileNotFound as err:
            raise err
        except Exception as err:
            raise err

    def get_config(self, tenant_id, graph_id, vnf_id, url):
        if not self.vnfService.is_vnf_started(tenant_id, graph_id, vnf_id):
            raise VnfNotStarted("Vnf is not started")
        address = self.vnfService.get_management_address(tenant_id, graph_id, vnf_id)
        if address is None:
            raise ManagementAddressNotFound("Management address of vnf's agent not found")
        try:
            request_url = "http://" + address + '/' + tenant_id + '/' + graph_id + '/' + vnf_id + '/' + url
            self.configurationService.get(request_url)
        except HTTPError as err:
            if err.response.status_code == 404:
                request_url = "http://" + address + '/' + url
                try:
                    return self.configurationService.get(request_url)
                except HTTPError as err:
                    raise err
            else:
                raise err
        except Exception as ex:
            raise ex

    def put_config(self, tenant_id, graph_id, vnf_id, url, data):
        if not self.vnfService.is_vnf_started(tenant_id, graph_id, vnf_id):
            raise VnfNotStarted("Vnf is not started")
        address = self.vnfService.get_management_address(tenant_id, graph_id, vnf_id)
        if address is None:
            raise ManagementAddressNotFound("Management address of vnf's agent not found")
        try:
            request_url = "http://" + address + '/' + tenant_id + '/' + graph_id + '/' + vnf_id + '/' + url
            self.configurationService.put(request_url, data)
        except HTTPError as err:
            if err.response.status_code == 404:
                request_url = "http://" + address + '/' + url
                try:
                    return self.configurationService.put(request_url, data)
                except HTTPError as err:
                    raise err
            else:
                raise err
        except Exception as ex:
            raise ex

    def delete_config(self, tenant_id, graph_id, vnf_id, url):
        pass