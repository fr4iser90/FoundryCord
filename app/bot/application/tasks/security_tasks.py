# In application/tasks/security_tasks.py
async def schedule_key_rotation():
    """Schedule periodic key rotation checks"""
    while True:
        key_service = ServiceFactory.get_key_rotation_service()
        if await key_service.should_rotate_keys():
            await KeyManager().rotate_keys()
            logger.info("Security keys have been rotated")
        
        # Check every 24 hours
        await asyncio.sleep(86400)