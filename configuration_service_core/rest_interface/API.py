from configuration_service_core import service
import threading
from configuration_service_core.pending_configuration import configuration_manager_singleton_factory
from configuration_service_core.pending_configuration import CallbackInterface
from configuration_service_core.pending_configuration import CallbackConditionInterface
from configuration_service_core.pending_configuration import ContractType
import time


def get_status_vnf(vnf_id, graph_id, tenant_id):
    service.get_status_vnf(vnf_id, graph_id, tenant_id)


def get_yang_from_vnf_id(vnf_type):
    service.get_yang_from_vnf_id(vnf_type)


def configure_vnf(configuration, vnf_id, graph_id, tenant_id):
    if not service.get_vnf_agent_state(vnf_id=vnf_id, graph_id=graph_id, tenant_id=tenant_id):
        service.configure_vnf(configuration, vnf_id, tenant_id, graph_id)
        return 202
    event = threading.Event()
    configuration_callback = ConfigurationCallback(event)
    configuration_callback_condition = ConfigurationCallbackCondition(vnf_id)
    configuration_manager_singleton_factory().set_on_configuration_ack(condition=configuration_callback_condition,
                                                                       functor=configuration_callback,
                                                                       contract_type=ContractType.TEMPORARY)
    event.clear()
    service.configure_vnf(configuration, vnf_id, tenant_id, graph_id)
    if not event.wait(20):
        configuration_manager_singleton_factory().remove_on_configuration_ack(condition=configuration_callback_condition,
                                                                              functor=configuration_callback,
                                                                              contract_type=ContractType.TEMPORARY)
        return 503
    return 200


class ConfigurationCallback(CallbackInterface):
    def __init__(self, event):
        self.event = event

    def execute(self, configuration):
        self.event.set()

    def compare(self, condition):
        if self.event == condition.event:
            return True
        return False


class ConfigurationCallbackCondition(CallbackConditionInterface):
    def __init__(self, vnf_id):
        self.vnf_id = vnf_id

    def check(self, configuration):
        if configuration.vnf_id == self.vnf_id:
            return True
        return False

    def compare(self, callback):
        if self.vnf_id == callback.vnf_id:
            return True
        return False
