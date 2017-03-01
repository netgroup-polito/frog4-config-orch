from enum import Enum
from threading import Lock


class ConfigurationManager:
    def __init__(self):
        self.list_pending_configuration = []
        self.on_syn = []
        self.on_ack = []
        self.pending_configuration_lock = Lock()
        self.on_ack_lock = Lock()

    def configuration_syn(self, vnf_id, graph_id, tenant_id, configuration):
        self.pending_configuration_lock.acquire()
        self.list_pending_configuration.append(Configuration(vnf_id=vnf_id, graph_id=graph_id, tenant_id=tenant_id, configuration=configuration))
        self.pending_configuration_lock.release()

    def configuration_ack(self, vnf_id, graph_id, tenant_id):
        configuration = None
        self.pending_configuration_lock.acquire()
        for conf in self.list_pending_configuration:
            if conf.vnf_id.split('.')[1] == vnf_id:
                configuration = conf
                break
        if configuration is None:
            self.pending_configuration_lock.release()
            return

        self.list_pending_configuration.remove(configuration)
        self.pending_configuration_lock.release()
        self.on_ack_lock.acquire()
        for callback in self.on_ack:
            if callback.condition:
                callback.functor.execute(configuration)
                if callback.contract_type == ContractType.TEMPORARY:
                    self.on_ack.remove(callback)
        self.on_ack_lock.release()

    def set_on_configuration_ack(self, condition, functor, contract_type):
        """
        set a method to call each time a configuration ack is received
        the method stored into the functor is called only if the condition is satisfied
        the lifecycle of the functor is due to the contract_type
        :param condition:
        :param functor:
        :return:
        """
        self.on_ack_lock.acquire()
        self.on_ack.append(CallbackInformation(condition=condition, functor=functor, contract_type=contract_type))
        self.on_ack_lock.release()

    def remove_on_configuration_ack(self, condition, functor, contract_type):
        self.on_ack_lock.acquire()
        for callback in self.on_ack:
            if isinstance(condition, type(callback.condition)) and condition.compare(callback.condition):
                if isinstance(functor, type(callback.functor))and functor.compare(callback.functor):
                    if contract_type == callback.contract_type:
                        self.on_ack.remove(callback)
                        self.on_ack_lock.release()
                        return
        self.on_ack_lock.release()

    def set_on_configuration_syn(self, condition, functor, contract_type):
        """
        set a method to call each time a configuration is sent to a vnf
        the method stored into the functor is called only if the condition is satisfied
        the lifecycle of the functor is due to the contract_type
        :param condition:
        :param functor:
        :return:
        """
        self.on_syn.append(CallbackInformation(condition=condition, functor=functor, contract_type=contract_type))

    def remove_on_configuration_syn(self, condition, functor, contract_type):
        for callback in self.on_syn:
            if isinstance(condition, type(callback.condition)) and condition.compare(callback.condition):
                if isinstance(functor, type(callback.functor)) and functor.compare(callback.functor):
                    if contract_type == callback.contract_type:
                        self.on_syn.remove(callback)
                        return


class CallbackInformation:
    def __init__(self, condition, functor, contract_type):
        self.condition = condition
        self.functor = functor
        self.contract_type = contract_type


class CallbackInterface:
    """
    configuration is an object of type Configuration (vnf_id, graph_id, tenant_id, configuration)
    """
    def execute(self, configuration): pass

    def compare(self, callback):
        """
            Method used in order to remove a callback from an event list
            eventually you have to compare all the attributes of the instance which the class implementing 'CallbackConditionInterface' set into the constructor
            :param condition:
            :return:
        """
        pass


class CallbackConditionInterface:
    """
    Such an interface defines how to implement a condition method in order to specify when to trigger a callback
    It has to return a boolean
    The check method receive a Configuration object as first parameter (vnf_id, graph_id, tenant_id, configuration)
    """
    def check(self, configuration): pass

    def compare(self, condition):
        """
        Method used in order to remove a callback from an event list
        eventually you have to compare all the attributes of the instance which the class implementing 'CallbackConditionInterface' set into the constructor
        :param condition:
        :return:
        """
        pass


class Configuration:
    def __init__(self, vnf_id, graph_id, tenant_id, configuration=None):
        self.vnf_id = vnf_id
        self.graph_id = "graphid"
        self.tenant_id = "tenantid"
        self.configuration = configuration


def configuration_manager_singleton_factory(_singleton=ConfigurationManager()):
    return _singleton


class ContractType(Enum):
    '''
    It lists the lifecycle of a callback
    TEMPORARY: the callback is called only the first time the condition is true
    PERMANENT: the callback is called all the times the condition is true
    '''
    TEMPORARY = 1,
    PERMANENT = 2
