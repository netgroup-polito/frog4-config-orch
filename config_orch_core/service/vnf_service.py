from config_orch_core.model.vnf import VNF
from config_orch_core.repository.vnf_repo import VnfRepo

class VnfService():

    def __init__(self):
        self.vnf_repo = VnfRepo()

    def clean_db(self):
        self.vnf_repo.clean_db()

    def is_vnf_started(self, tenant_id, graph_id, vnf_id):
        vnf = VNF(tenant_id, graph_id, vnf_id)
        try:
            return self.vnf_repo.is_vnf_started(vnf)
        except IOError:
            raise IOError

    def get_started_vnf(self):
        try:
            return self.vnf_repo.get_started_vnf()
        except IOError:
            raise IOError

    def save_started_vnf(self, tenant_id, graph_id, vnf_id):
        vnf = VNF(tenant_id, graph_id, vnf_id)
        try:
            self.vnf_repo.save_started_vnf(vnf)
        except IOError:
            raise IOError

    def save_management_address(self, tenant_id, graph_id, vnf_id, address):
        vnf = VNF(tenant_id, graph_id, vnf_id)
        try:
            self.vnf_repo.save_management_address(vnf, address)
        except IOError:
            raise IOError

    def get_management_address(self, tenant_id, graph_id, vnf_id):
        vnf = VNF(tenant_id, graph_id, vnf_id)
        try:
            return self.vnf_repo.get_management_address(vnf)
        except IOError:
            raise IOError