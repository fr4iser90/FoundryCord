from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

class KeyRepository(ABC):
    @abstractmethod
    async def initialize(self) -> bool:
        pass
    
    @abstractmethod
    async def get_key(self, key_name: str) -> Optional[str]:
        pass
    
    @abstractmethod
    async def store_key(self, key_name: str, key_value: str) -> bool:
        pass
    
    @abstractmethod
    async def delete_key(self, key_name: str) -> bool:
        pass
    
    @abstractmethod
    async def get_jwt_secret_key(self) -> Optional[str]:
        pass
    
    @abstractmethod
    async def save_jwt_secret_key(self, key: str) -> bool:
        pass
    
    @abstractmethod
    async def get_aes_key(self) -> Optional[str]:
        pass
    
    @abstractmethod
    async def save_aes_key(self, key: str) -> bool:
        pass