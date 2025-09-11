#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
💾 Frenly AI Cache Manager
Advanced caching system for AI responses and model outputs
"""

import asyncio
import logging
import time
import json
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import redis
import aioredis
from backend.config import get_config

logger = logging.getLogger(__name__)

class CacheType(Enum):
    """Cache type enumeration"""
    RESPONSE = "response"
    MODEL_OUTPUT = "model_output"
    EMBEDDING = "embedding"
    SESSION = "session"
    METADATA = "metadata"

class CacheStrategy(Enum):
    """Cache strategy enumeration"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    SIZE = "size"  # Size-based eviction

@dataclass
class CacheEntry:
    """Cache entry definition"""
    key: str
    value: Any
    cache_type: CacheType
    created_at: str
    last_accessed: str
    access_count: int = 0
    ttl: int = 3600
    size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheConfig:
    """Cache configuration"""
    max_size: int = 10000
    default_ttl: int = 3600
    strategy: CacheStrategy = CacheStrategy.LRU
    enable_compression: bool = True
    enable_serialization: bool = True
    cleanup_interval: int = 300
    memory_threshold: float = 0.8

class CacheManager:
    """Advanced caching system for Frenly AI"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.cache_config = CacheConfig()
        self.redis_client = None
        self.local_cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        self.running = False
        
        logger.info("✅ Cache Manager initialized")
    
    async def start(self):
        """Start the cache manager"""
        self.running = True
        logger.info("🚀 Starting Cache Manager...")
        
        try:
            # Initialize Redis connection
            self.redis_client = aioredis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
            
            # Start cache maintenance tasks
            asyncio.create_task(self._cleanup_expired_entries())
            asyncio.create_task(self._monitor_cache_usage())
            asyncio.create_task(self._sync_to_redis())
            
            logger.info("✅ Cache Manager started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Cache Manager: {e}")
            # Continue with local cache only
            self.redis_client = None
    
    async def stop(self):
        """Stop the cache manager"""
        self.running = False
        logger.info("🛑 Stopping Cache Manager...")
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("✅ Cache Manager stopped")
    
    async def get(self, key: str, cache_type: CacheType = CacheType.RESPONSE) -> Optional[Any]:
        """Get value from cache"""
        self.cache_stats["total_requests"] += 1
        
        try:
            # Try local cache first
            if key in self.local_cache:
                entry = self.local_cache[key]
                
                # Check if entry is expired
                if self._is_expired(entry):
                    await self._remove_entry(key)
                    self.cache_stats["misses"] += 1
                    return None
                
                # Update access info
                entry.last_accessed = datetime.now().isoformat()
                entry.access_count += 1
                
                self.cache_stats["hits"] += 1
                logger.debug(f"Cache hit (local): {key}")
                return entry.value
            
            # Try Redis cache
            if self.redis_client:
                redis_key = f"frenly_cache:{cache_type.value}:{key}"
                cached_data = await self.redis_client.get(redis_key)
                
                if cached_data:
                    entry_data = json.loads(cached_data)
                    entry = CacheEntry(**entry_data)
                    
                    # Check if entry is expired
                    if self._is_expired(entry):
                        await self.redis_client.delete(redis_key)
                        self.cache_stats["misses"] += 1
                        return None
                    
                    # Update access info
                    entry.last_accessed = datetime.now().isoformat()
                    entry.access_count += 1
                    
                    # Store in local cache
                    self.local_cache[key] = entry
                    
                    self.cache_stats["hits"] += 1
                    logger.debug(f"Cache hit (redis): {key}")
                    return entry.value
            
            self.cache_stats["misses"] += 1
            logger.debug(f"Cache miss: {key}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting cache entry {key}: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, cache_type: CacheType = CacheType.RESPONSE, 
                  ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.cache_config.default_ttl
            current_time = datetime.now().isoformat()
            
            # Calculate size
            size = self._calculate_size(value)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                cache_type=cache_type,
                created_at=current_time,
                last_accessed=current_time,
                ttl=ttl,
                size=size,
                metadata=metadata or {}
            )
            
            # Store in local cache
            self.local_cache[key] = entry
            
            # Store in Redis if available
            if self.redis_client:
                redis_key = f"frenly_cache:{cache_type.value}:{key}"
                entry_data = {
                    "key": entry.key,
                    "value": entry.value,
                    "cache_type": entry.cache_type.value,
                    "created_at": entry.created_at,
                    "last_accessed": entry.last_accessed,
                    "access_count": entry.access_count,
                    "ttl": entry.ttl,
                    "size": entry.size,
                    "metadata": entry.metadata
                }
                
                await self.redis_client.setex(
                    redis_key,
                    ttl,
                    json.dumps(entry_data, default=str)
                )
            
            # Check if eviction is needed
            await self._check_eviction()
            
            logger.debug(f"Cache set: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting cache entry {key}: {e}")
            return False
    
    async def delete(self, key: str, cache_type: CacheType = CacheType.RESPONSE) -> bool:
        """Delete value from cache"""
        try:
            # Remove from local cache
            if key in self.local_cache:
                del self.local_cache[key]
            
            # Remove from Redis
            if self.redis_client:
                redis_key = f"frenly_cache:{cache_type.value}:{key}"
                await self.redis_client.delete(redis_key)
            
            logger.debug(f"Cache deleted: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting cache entry {key}: {e}")
            return False
    
    async def clear(self, cache_type: Optional[CacheType] = None) -> bool:
        """Clear cache entries"""
        try:
            if cache_type:
                keys_to_remove = [
                    key for key, entry in self.local_cache.items()
                    if entry.cache_type == cache_type
                ]
                for key in keys_to_remove:
                    del self.local_cache[key]
                
                if self.redis_client:
                    pattern = f"frenly_cache:{cache_type.value}:*"
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
            else:
                # Clear all cache
                self.local_cache.clear()
                
                if self.redis_client:
                    pattern = "frenly_cache:*"
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
            
            logger.info(f"Cache cleared: {cache_type.value if cache_type else 'all'}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error clearing cache: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.local_cache)
        total_size = sum(entry.size for entry in self.local_cache.values())
        
        hit_rate = 0.0
        if self.cache_stats["total_requests"] > 0:
            hit_rate = self.cache_stats["hits"] / self.cache_stats["total_requests"]
        
        return {
            "total_entries": total_entries,
            "total_size": total_size,
            "hit_rate": hit_rate,
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "evictions": self.cache_stats["evictions"],
            "total_requests": self.cache_stats["total_requests"],
            "cache_types": {
                cache_type.value: len([
                    entry for entry in self.local_cache.values()
                    if entry.cache_type == cache_type
                ])
                for cache_type in CacheType
            }
        }
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired"""
        created_at = datetime.fromisoformat(entry.created_at)
        return datetime.now() - created_at > timedelta(seconds=entry.ttl)
    
    def _calculate_size(self, value: Any) -> int:
        """Calculate size of value in bytes"""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (int, float, bool)):
                return 8
            elif isinstance(value, (list, dict)):
                return len(json.dumps(value).encode('utf-8'))
            else:
                return len(pickle.dumps(value))
        except:
            return 1024  # Default size
    
    async def _check_eviction(self):
        """Check if eviction is needed"""
        if len(self.local_cache) <= self.cache_config.max_size:
            return
        
        # Evict entries based on strategy
        if self.cache_config.strategy == CacheStrategy.LRU:
            await self._evict_lru()
        elif self.cache_config.strategy == CacheStrategy.LFU:
            await self._evict_lfu()
        elif self.cache_config.strategy == CacheStrategy.TTL:
            await self._evict_ttl()
        elif self.cache_config.strategy == CacheStrategy.SIZE:
            await self._evict_size()
    
    async def _evict_lru(self):
        """Evict least recently used entries"""
        # Sort by last accessed time
        sorted_entries = sorted(
            self.local_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove oldest entries
        entries_to_remove = len(self.local_cache) - self.cache_config.max_size + 100
        for i in range(min(entries_to_remove, len(sorted_entries))):
            key, entry = sorted_entries[i]
            await self._remove_entry(key)
    
    async def _evict_lfu(self):
        """Evict least frequently used entries"""
        # Sort by access count
        sorted_entries = sorted(
            self.local_cache.items(),
            key=lambda x: x[1].access_count
        )
        
        # Remove least used entries
        entries_to_remove = len(self.local_cache) - self.cache_config.max_size + 100
        for i in range(min(entries_to_remove, len(sorted_entries))):
            key, entry = sorted_entries[i]
            await self._remove_entry(key)
    
    async def _evict_ttl(self):
        # Sort by TTL
        sorted_entries = sorted(
            self.local_cache.items(),
            key=lambda x: x[1].ttl
        )
        
    
    async def _evict_size(self):
        """Evict largest entries"""
        # Sort by size
        sorted_entries = sorted(
            self.local_cache.items(),
            key=lambda x: x[1].size,
            reverse=True
        )
        
        # Remove largest entries
        entries_to_remove = len(self.local_cache) - self.cache_config.max_size + 100
        for i in range(min(entries_to_remove, len(sorted_entries))):
            key, entry = sorted_entries[i]
            await self._remove_entry(key)
    
    async def _remove_entry(self, key: str):
        """Remove entry from cache"""
        if key in self.local_cache:
            entry = self.local_cache[key]
            del self.local_cache[key]
            
            # Remove from Redis
            if self.redis_client:
                redis_key = f"frenly_cache:{entry.cache_type.value}:{key}"
                await self.redis_client.delete(redis_key)
            
            self.cache_stats["evictions"] += 1
    
    async def _cleanup_expired_entries(self):
        """Clean up expired entries"""
        while self.running:
            try:
                current_time = datetime.now()
                expired_keys = []
                
                for key, entry in self.local_cache.items():
                    if self._is_expired(entry):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    await self._remove_entry(key)
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                await asyncio.sleep(self.cache_config.cleanup_interval)
                
            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_cache_usage(self):
        """Monitor cache usage and performance"""
        while self.running:
            try:
                stats = await self.get_stats()
                
                # Log cache statistics
                logger.info(f"Cache stats: {stats['total_entries']} entries, "
                           f"{stats['total_size']} bytes, "
                           f"hit rate: {stats['hit_rate']:.2%}")
                
                # Check memory threshold
                if stats['total_size'] > self.cache_config.memory_threshold * 1024 * 1024 * 1024:  # 1GB
                    logger.warning("⚠️ Cache memory usage high, triggering eviction")
                    await self._check_eviction()
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"❌ Cache monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _sync_to_redis(self):
        """Sync local cache to Redis"""
        while self.running:
            try:
                if not self.redis_client:
                    await asyncio.sleep(60)
                    continue
                
                # Sync recent entries to Redis
                recent_entries = [
                    entry for entry in self.local_cache.values()
                    if datetime.now() - datetime.fromisoformat(entry.last_accessed) < timedelta(minutes=5)
                ]
                
                for entry in recent_entries:
                    redis_key = f"frenly_cache:{entry.cache_type.value}:{entry.key}"
                    entry_data = {
                        "key": entry.key,
                        "value": entry.value,
                        "cache_type": entry.cache_type.value,
                        "created_at": entry.created_at,
                        "last_accessed": entry.last_accessed,
                        "access_count": entry.access_count,
                        "ttl": entry.ttl,
                        "size": entry.size,
                        "metadata": entry.metadata
                    }
                    
                    await self.redis_client.setex(
                        redis_key,
                        entry.ttl,
                        json.dumps(entry_data, default=str)
                    )
                
                await asyncio.sleep(30)  # Sync every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Cache sync error: {e}")
                await asyncio.sleep(60)

# Global cache manager instance
cache_manager = CacheManager()
