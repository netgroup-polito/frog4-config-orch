import json
from rest_framework.parsers import JSONParser
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from configuration_service_core.rest_interface import API
from rest_framework.parsers import ParseError

from configuration_service_core import service
from configuration_service_core.log import print_log
from django.core.servers.basehttp import FileWrapper

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


def RetrieveFileList(request, vnf_id, graph_id, tenant_id):
    print_log("RetrieveFileList")
    if request.method == "GET":
        try:
            result = service.get_file_list(vnf_id, graph_id, tenant_id)
        except Exception as ex:
            print_log("[RetrieveFileList] Exception: " + str(ex))
            return HttpResponse(status=503)
        serialized_obj = json.dumps(result)
        return HttpResponse("%s" % serialized_obj, status=200, content_type="application/json")
    else:
        return HttpResponse(status=501)



def RetrieveFile(request, filename, vnf_id, graph_id, tenant_id):
    print_log("RetrieveFile: " + filename)
    if request.method == "GET":
        try:
            file = service.get_file(filename, vnf_id, graph_id, tenant_id)
        except Exception as ex:
            print_log("[RetrieveFile] Exception: " + str(ex))
            return HttpResponse(status=204)
        response = HttpResponse(FileWrapper(file), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response
    else:
        return HttpResponse(status=501)




