import abc

class ComponentRegistry(abc.ABC):
    @abc.abstractmethod
    def register_component(self, component_type, component_class, description, default_config):
        pass

    @abc.abstractmethod
    def get_component_class(self, component_type):
        pass

    @abc.abstractmethod
    def get_type_by_key(self, component_key):
        pass

    @abc.abstractmethod
    def get_definition_by_key(self, component_key):
        pass

    @abc.abstractmethod
    def get_all_component_types(self):
        pass

    @abc.abstractmethod
    def has_component(self, component_type):
        pass 