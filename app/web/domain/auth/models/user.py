from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str
    username: str 
    avatar: Optional[str] 