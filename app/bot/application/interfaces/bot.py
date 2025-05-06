import abc
# Forward declarations for type checking if needed, but not for runtime use
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     import asyncio
#     import nextcord
#     from .service_factory import ServiceFactory # Assuming ServiceFactory is the interface name

class Bot(abc.ABC):
    @property
    @abc.abstractmethod
    def service_factory(self):
        # Should return an instance of ServiceFactory (interface)
        pass

    @property
    @abc.abstractmethod
    def user(self):
        # Should return nextcord.User or ClientUser
        pass

    @abc.abstractmethod
    def get_channel(self, id):
        pass

    @abc.abstractmethod
    def get_guild(self, id):
        pass 