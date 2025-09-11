import redis
import logging
from core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client = None

def get_redis_client():
    """Get Redis client instance"""
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                password=getattr(settings, 'REDIS_PASSWORD', None),
                decode_responses=True
            )
            
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
    
    return _redis_client

    
    def __init__(self):
        self._data = {}
    
    def ping(self):
        return True
    
    def get(self, key):
        return self._data.get(key)
    
    def setex(self, key, time, value):
        self._data[key] = value
        return True
    
    def publish(self, channel, message):
        return 1
    
    def pubsub(self):

    
    def __init__(self):
        self._subscribed = False
    
    async def subscribe(self, channel):
        self._subscribed = True
    
    async def listen(self):
