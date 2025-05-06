import abc

class ServiceFactory(abc.ABC):
    @abc.abstractmethod
    def register_service_creator(self, name, creator, overwrite):
        pass

    @abc.abstractmethod
    def register_service(self, name, instance, overwrite):
        pass

    @abc.abstractmethod
    def get_service(self, name):
        pass

    @abc.abstractmethod
    def has_service(self, name):
        pass

    @abc.abstractmethod
    def get_all_services(self):
        pass 