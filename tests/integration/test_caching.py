import pytest
import sys
import os
import time

# Try to import Redis
try:
    import redis
    REDIS_IMPORT_SUCCESS = True
except ImportError:
    REDIS_IMPORT_SUCCESS = False

@pytest.mark.skipif(not REDIS_IMPORT_SUCCESS, reason="Redis module could not be imported")
class TestRedisCache:
    @pytest.fixture
    def redis_client(self):
        """Create a Redis client for testing"""
        try:
            client = redis.Redis(
                host=os.environ.get('REDIS_HOST', 'homelab-redis'),
                port=int(os.environ.get('REDIS_PORT', '6379')),
                db=int(os.environ.get('REDIS_DB', '0')),
                decode_responses=True
            )
            # Check connection
            client.ping()
            return client
        except redis.ConnectionError:
            pytest.skip("Redis connection failed - skipping tests")
    
    def test_set_get(self, redis_client):
        """Test basic set/get operations"""
        test_key = "test:key:1"
        test_value = "test-value-1"
        
        # Set a value
        redis_client.set(test_key, test_value)
        
        # Get the value back
        result = redis_client.get(test_key)
        
        # Clean up
        redis_client.delete(test_key)
        
        # Assert
        assert result == test_value, f"Expected {test_value}, got {result}"
    
    def test_expiry(self, redis_client):
        """Test key expiration"""
        test_key = "test:key:expiry"
        test_value = "test-value-expiry"
        
        # Set with 1 second expiry
        redis_client.set(test_key, test_value, ex=1)
        
        # Value should exist initially
        assert redis_client.get(test_key) == test_value
        
        # Wait for expiry
        time.sleep(1.5)
        
        # Value should be gone
        assert redis_client.get(test_key) is None, "Key should have expired" 