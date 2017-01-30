import json
from configparser import SafeConfigParser

from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from configuration_service_core import service
from configuration_service_core.log import print_log

#conf_server = server.ConfigurationServer()
#conf_server.start()


class ConfigureVNF(APIView):
    def put(self, request, vnf_id, graph_id, tenant_id):

        """
        Send the configuration to the VNF agent
        :param request:
        :param vnf_id:
        :param graph_id:
        :param tenant_id:
        :return:
        """
        status = service.configure_vnf(request, vnf_id, tenant_id, graph_id)
        return HttpResponse(status=200)


class RetrieveStatus(APIView):
    def get(self, request, vnf_id, graph_id, tenant_id):
        """
        Retrieve the actual status of the VNF
        :param request:
        :param vnf_id:
        :param graph_id:
        :param tenant_id:
        :return:
        """
        status = service.get_status_vnf(vnf_id, graph_id, tenant_id)
        if status == "":
            return HttpResponse(status=404)
        return Response(data=json.loads(status))


class YANGModels(APIView):
    '''
    '''
    def get(self, request, vnf_type):
        """
        Retrieve the YANG file of the vnf_type type (for the GUI)
        :param request:
        :param vnf_type:
        :return:
        """
        yang = service.get_yang_from_vnf_id(vnf_type)
        if yang == "":
            return HttpResponse(status=404)
        return Response(data=json.loads(yang))
