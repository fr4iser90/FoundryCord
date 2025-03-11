# In domain/security/services/key_rotation_service.py
class KeyRotationService:
    """Domain service that defines when and how keys should rotate"""
    
    def __init__(self, key_repository):
        self.key_repository = key_repository
    
    async def should_rotate_keys(self):
        """Business logic for determining key rotation"""
        last_rotation = await self.key_repository.get_last_rotation_time()
        # Apply business rules for rotation
        return self._check_rotation_policy(last_rotation)
        
    def _check_rotation_policy(self, last_rotation):
        """Implement business rules for key rotation"""