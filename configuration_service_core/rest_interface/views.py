import json
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from configuration_service_core.rest_interface import API
from rest_framework.parsers import ParseError


class ConfigureVNF(APIView):
    parser_classes = (JSONParser,)

    def put(self, request, vnf_id, graph_id, tenant_id):
        """
        Send the configuration to the VNF agent
        :param request:
        :param vnf_id:
        :param graph_id:
        :param tenant_id:
        :return:
        """
        if request.META['CONTENT_TYPE'] != 'application/json':
            return HttpResponse(status=415)
        data = request.stream.read()
        if data == "":
            raise ParseError(detail="no yang was provided")
        status = API.configure_vnf(data.decode(), vnf_id, graph_id, tenant_id)
        return HttpResponse(status=status)


class RetrieveStatus(APIView):
    parser_classes = (JSONParser,)

    def get(self, request, vnf_id, graph_id, tenant_id):
        """
        Retrieve the actual status of the VNF
        :param request:
        :param vnf_id:
        :param graph_id:
        :param tenant_id:
        :return:
        """
        status = API.get_status_vnf(vnf_id, graph_id, tenant_id)
        if status == "":
            return HttpResponse(status=404)
        return Response(data=json.loads(status))
