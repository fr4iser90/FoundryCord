import pytest
import sys
import os
import time

# Try to import Redis - conditional testing based on availability
try:
    import redis
    REDIS_IMPORT_SUCCESS = True
except ImportError:
    REDIS_IMPORT_SUCCESS = False

@pytest.mark.skipif(not REDIS_IMPORT_SUCCESS, reason="Redis module could not be imported")
class TestRedisCache:
    """Test suite for Redis caching functionality
    
    These tests verify that the application can properly interact with Redis,
    which serves as the primary caching layer. Tests include basic operations,
    expiry functionality, and hash manipulation.
    
    All tests are skipped if Redis cannot be imported or connected to.
    """
    
    @pytest.fixture
    def redis_client(self):
        """Create a Redis client for testing
        
        This fixture establishes a connection to the Redis server using
        environment-based configuration. It includes timeout settings to
        fail fast if Redis is unavailable.
        
        The test is skipped if connection cannot be established.
        """
        try:
            # Use the Docker network service name for Redis
            client = redis.Redis(
                host=os.environ.get('REDIS_HOST', 'homelab-redis'),  # Container name in Docker network
                port=int(os.environ.get('REDIS_PORT', '6379')),      # Default Redis port
                db=int(os.environ.get('REDIS_DB', '0')),             # Database number
                decode_responses=True,                               # Auto-decode Redis responses to strings
                socket_timeout=2.0,                                  # Add timeout to fail faster if Redis is unavailable
                socket_connect_timeout=2.0                           # Connection timeout
            )
            # Verify connection is working with a ping
            client.ping()
            return client
        except (redis.ConnectionError, redis.TimeoutError) as e:
            pytest.skip(f"Redis connection failed - skipping tests: {e}")
    
    def test_set_get(self, redis_client):
        """Test basic set/get operations
        
        Verifies that the most fundamental Redis operations work correctly:
        - Setting a value with a key
        - Retrieving the value by its key
        - Proper cleanup by deleting the key
        """
        test_key = "test:key:1"
        test_value = "test-value-1"
        
        # Set a value
        redis_client.set(test_key, test_value)
        
        # Get the value back
        result = redis_client.get(test_key)
        
        # Clean up - important for test isolation
        redis_client.delete(test_key)
        
        # Assert
        assert result == test_value, f"Expected {test_value}, got {result}"
    
    def test_expiry(self, redis_client):
        """Test key expiration
        
        Verifies that Redis correctly implements the expiration mechanism:
        1. Key is available immediately after setting with expiry
        2. Key is automatically removed after the expiry time
        
        This is critical for cache invalidation functionality.
        """
        test_key = "test:key:expiry"
        test_value = "test-value-expiry"
        
        # Set with 1 second expiry
        redis_client.set(test_key, test_value, ex=1)
        
        # Value should exist initially
        assert redis_client.get(test_key) == test_value
        
        # Wait for expiry - slightly longer than expiry time to account for timing variations
        time.sleep(1.5)
        
        # Value should be gone
        assert redis_client.get(test_key) is None, "Key should have expired"
        
    def test_hash_operations(self, redis_client):
        """Test hash operations in Redis
        
        Verifies that Redis hash functionality works correctly:
        - Setting multiple hash fields at once
        - Retrieving a single field
        - Retrieving all fields
        
        Hashes are used for structured data caching in the application.
        """
        test_key = "test:hash:1"
        test_hash = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        
        # Set multiple hash fields
        for field, value in test_hash.items():
            redis_client.hset(test_key, field, value)
        
        # Get individual field
        assert redis_client.hget(test_key, "field1") == "value1"
        
        # Get all fields
        result = redis_client.hgetall(test_key)
        assert result == test_hash
        
        # Delete hash - cleanup
        redis_client.delete(test_key) 