from enum import Enum

class ResponseMode(Enum):
    DM = "dm"
    EPHEMERAL = "ephemeral"
    ENCRYPTED_EPHEMERAL = "encrypted_ephemeral"
    
ACTIVE_RESPONSE_MODE = ResponseMode.ENCRYPTED_EPHEMERAL