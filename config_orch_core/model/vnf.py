class VNF():

    def __init__(self, tenant_id=None,
                       graph_id=None,
                       vnf_id=None,
                       address=None):

        self.tenant_id = tenant_id
        self.graph_id = graph_id
        self.vnf_id = vnf_id
        self.address = address


    def __str__(self):
        str = "{"
        if self.tenant_id is not None:
            str += "'tenant_id': " + self.tenant_id + ", "
        if self.graph_id is not None:
            str += "'graph_id': " + self.graph_id + ", "
        if self.vnf_id is not None:
            str += "'vnf_id': " + self.vnf_id + ", "
        if self.address is not None:
            str += "'address': " + self.address + ", "
        str += "}"
        return str

    def __eq__(self, other):
        if self.tenant_id != other.tenant_id:
            return False
        if self.graph_id != other.graph_id:
            return False
        if self.vnf_id != other.vnf_id:
            return False
        return True

    def toJson(self):
        vnf_dict = {}
        vnf_dict['tenant_id'] = self.tenant_id
        vnf_dict['graph_id'] = self.graph_id
        vnf_dict['vnf_id'] = self.vnf_id
        if self.address is not None:
            vnf_dict['address'] = self.address
        return vnf_dict
