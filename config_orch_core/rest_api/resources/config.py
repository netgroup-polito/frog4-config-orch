import json
import logging
from requests.exceptions import HTTPError

from flask import request, Response, send_from_directory
from flask_restplus import Resource

from config_orch_core.exception.file_not_found import FileNotFound
from config_orch_core.exception.functional_capability_not_found import FunctionalCapabilityNotFound
from config_orch_core.exception.vnf_not_started import VnfNotStarted
from config_orch_core.exception.management_address_not_found import ManagementAddressNotFound
from config_orch_core.controller.main_controller import MainController
from config_orch_core.rest_api.api import api

root_ns = api.namespace('config', 'Global Resource')

@root_ns.route('/started_vnf', methods=['GET'])
class Vnf(Resource):
    @root_ns.response(200, 'Started vnf retrieved')
    @root_ns.response(500, 'Internal Error')
    def get(self):
        mainController = MainController()
        try:
            json_data = json.dumps(mainController.get_started_vnf())
            return Response(json_data, status=200, mimetype="application/json")

        except IOError as err:
            logging.debug(err)
            return Response(json.dumps(str(err)), status=500, mimetype="application/json")
        except Exception as err:
            logging.debug(err)
            return Response(json.dumps(str(err)), status=500, mimetype="application/json")

@root_ns.route('/<tenant_id>/<graph_id>/<vnf_id>/', methods=['GET','PUT'])
@root_ns.route('/<tenant_id>/<graph_id>/<vnf_id>/<url>', methods=['GET','PUT'])
class Configuration(Resource):
    @root_ns.response(200, 'Ok')
    @root_ns.response(404, 'Not Found')
    @root_ns.response(500, 'Internal Error')
    def get(self, tenant_id, graph_id, vnf_id, url=None):
        if url is None:
            url = ''
        mainController = MainController()
        try:
            return mainController.get_config(tenant_id, graph_id, vnf_id, url)

        except VnfNotStarted as err:
            return Response(json.dumps(err.get_mess()), status=404, mimetype="application/json")
        except ManagementAddressNotFound as err:
            return Response(json.dumps(err.get_mess()), status=500, mimetype="application/json")
        except HTTPError as err:
            return Response(json.dumps(str(err)), status=err.response.status_code, mimetype="application/json")
        except Exception as err:
            return Response(json.dumps(str(err)), status=500, mimetype="application/json")

    @root_ns.response(200, 'Ok')
    @root_ns.response(404, 'Not Found')
    @root_ns.response(500, 'Internal Error')
    def put(self, tenant_id, graph_id, vnf_id, url=None):
        if url is None:
            url = ''
        mainController = MainController()
        try:
            return mainController.put_config(tenant_id, graph_id, vnf_id, url, request.data.decode())

        except VnfNotStarted as err:
            return Response(json.dumps(err.get_mess()), status=404, mimetype="application/json")
        except ManagementAddressNotFound as err:
            return Response(json.dumps(err.get_mess()), status=500, mimetype="application/json")
        except HTTPError as err:
            return Response(json.dumps(str(err)), status=err.response.status_code, mimetype="application/json")
        except Exception as err:
            return Response(json.dumps(str(err)), status=500, mimetype="application/json")

@root_ns.route('/files/<functional_capability>', methods=['GET'])
@root_ns.route('/files/<functional_capability>/<filename>', methods=['GET'])
class FileByFunctionalCapability(Resource):
    @root_ns.response(200, 'Ok')
    @root_ns.response(404, 'Not Found')
    @root_ns.response(500, 'Internal Error')
    def get(self, functional_capability, filename=None):
        mainController = MainController()
        try:
            if filename is None:
                json_data = json.dumps(mainController.retrieve_file_list(functional_capability))
                return Response(json_data, status=200, mimetype="application/json")
            else:
                filepath = mainController.retrieve_file_default(functional_capability, filename)
                return send_from_directory('', filepath)

        except FunctionalCapabilityNotFound as err:
            return Response(json.dumps(err.get_mess()), status=404, mimetype="application/json")
        except FileNotFound as err:
            return Response(json.dumps(err.get_mess()), status=404, mimetype="application/json")
        except Exception as err:
            return Response(json.dumps(str(err)), status=500, mimetype="application/json")

@root_ns.route('/files/<tenant_id>/<graph_id>/<vnf_id>/<filename>', methods=['GET'])
class FileByTriple(Resource):
    @root_ns.response(200, 'Ok')
    @root_ns.response(404, 'Not Found')
    @root_ns.response(500, 'Internal Error')
    def get(self, tenant_id, graph_id, vnf_id, filename):
        mainController = MainController()
        try:
            filepath = mainController.retrieve_file(tenant_id, graph_id, vnf_id, filename)
            return send_from_directory('', filepath)

        except FileNotFound as err:
            return Response(json.dumps(err.get_mess()), status=404, mimetype="application/json")
        except Exception as err:
            return Response(json.dumps(str(err)), status=500, mimetype="application/json")


