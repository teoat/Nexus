#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
⚡ Performance Optimization Module
Comprehensive performance optimization for Nexus Platform
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Union
from functools import wraps
from contextlib import asynccontextmanager
import redis
import psycopg2
from psycopg2 import pool
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    endpoint: str
    method: str
    response_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: datetime
    status_code: int
    cache_hit: bool = False

class DatabaseConnectionPool:
    """Database connection pool for optimal performance"""
    
    def __init__(self, 
        """
          Init  
        
        
        Args:
            host: Description of host
            port: Description of port
            database: Description of database
            user: Description of user
            password: Description of password
            min_connections: Description of min_connections
            max_connections: Description of max_connections
    
        Example:
            TBD: Add usage example
        """
                 host: str = "localhost",
                 port: int = 5432,
                 database: str = "nexus",
                 user: str = "nexus",
                 password: str = "nexus",
                 min_connections: int = 5,
                 max_connections: int = 20):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize database connection pool"""
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                self.min_connections,
                self.max_connections,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info(f"Database connection pool initialized: {self.min_connections}-{self.max_connections} connections")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool"""
        try:
            return self.pool.getconn()
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    def return_connection(self, connection):
        """Return connection to pool"""
        try:
            self.pool.putconn(connection)
        except Exception as e:
            logger.error(f"Failed to return database connection: {e}")
    
    def close_all_connections(self):
        """Close all connections in pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("All database connections closed")

class RedisCache:
    """Redis-based caching system for optimal performance"""
    
    def __init__(self, 
        """
          Init  
        
        
        Args:
            host: Description of host
            port: Description of port
            db: Description of db
            password: Description of password
            max_connections: Description of max_connections
    
        Example:
            TBD: Add usage example
        """
                 host: str = "localhost",
                 port: int = 6379,
                 db: int = 0,
                 password: Optional[str] = None,
                 max_connections: int = 10):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.redis_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize Redis connection pool"""
        try:
            self.redis_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                max_connections=self.max_connections,
                decode_responses=True
            )
            logger.info(f"Redis connection pool initialized: {self.max_connections} connections")
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")
            # Fallback to in-memory cache
            self.redis_pool = None
    
    def get_redis_client(self):
        """Get Redis client from pool"""
        if self.redis_pool:
            return redis.Redis(connection_pool=self.redis_pool)
        return None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            client = self.get_redis_client()
            if client:
                value = client.get(key)
                if value:
                    return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            client = self.get_redis_client()
            if client:
                serialized_value = json.dumps(value, default=str)
                return client.setex(key, ttl, serialized_value)
            return False
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            client = self.get_redis_client()
            if client:
                return bool(client.delete(key))
            return False
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            client = self.get_redis_client()
            if client:
                return bool(client.exists(key))
            return False
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_select_query(query: str, limit: int = 100, offset: int = 0) -> str:
        """Optimize SELECT queries with pagination"""
        # Add LIMIT and OFFSET if not present
        if "LIMIT" not in query.upper():
            query += f" LIMIT {limit}"
        if "OFFSET" not in query.upper() and offset > 0:
            query += f" OFFSET {offset}"
        
        # Add query hints for better performance
        if "SELECT" in query.upper():
            # Add index hints for common patterns
            if "WHERE" in query.upper():
                query = query.replace("SELECT", "SELECT /*+ USE_INDEX */", 1)
        
        return query
    
    @staticmethod
    def create_index_suggestions(table_name: str, columns: List[str]) -> List[str]:
        """Generate index creation suggestions"""
        suggestions = []
        
        # Single column indexes
        for column in columns:
            suggestions.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_{column} ON {table_name} ({column});")
        
        # Composite indexes for common query patterns
        if len(columns) > 1:
            suggestions.append(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_composite ON {table_name} ({', '.join(columns)});")
        
        return suggestions

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.metrics: List[PerformanceMetrics] = []
        self.start_time = time.time()
    
    def record_metric(self, metric: PerformanceMetrics):
        """Record performance metric"""
        self.metrics.append(metric)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def get_average_response_time(self, endpoint: Optional[str] = None) -> float:
        """Get average response time for endpoint or all endpoints"""
        if endpoint:
            endpoint_metrics = [m for m in self.metrics if m.endpoint == endpoint]
        else:
            endpoint_metrics = self.metrics
        
        if not endpoint_metrics:
            return 0.0
        
        return sum(m.response_time for m in endpoint_metrics) / len(endpoint_metrics)
    
    def get_slowest_endpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest endpoints by average response time"""
        endpoint_times = {}
        
        for metric in self.metrics:
            key = f"{metric.method} {metric.endpoint}"
            if key not in endpoint_times:
                endpoint_times[key] = []
            endpoint_times[key].append(metric.response_time)
        
        # Calculate averages and sort
        averages = [
            {
                "endpoint": endpoint,
                "average_time": sum(times) / len(times),
                "request_count": len(times)
            }
            for endpoint, times in endpoint_times.items()
        ]
        
        return sorted(averages, key=lambda x: x["average_time"], reverse=True)[:limit]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.metrics:
            return {"error": "No metrics available"}
        
        total_requests = len(self.metrics)
        successful_requests = len([m for m in self.metrics if 200 <= m.status_code < 300])
        failed_requests = total_requests - successful_requests
        cache_hits = len([m for m in self.metrics if m.cache_hit])
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests) * 100,
            "cache_hit_rate": (cache_hits / total_requests) * 100,
            "average_response_time": self.get_average_response_time(),
            "uptime_seconds": time.time() - self.start_time,
            "slowest_endpoints": self.get_slowest_endpoints(5)
        }

def performance_monitor(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = _get_memory_usage()
        
        try:
            result = await func(*args, **kwargs)
            status_code = 200
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            end_time = time.time()
            end_memory = _get_memory_usage()
            
            # Record performance metric
            metric = PerformanceMetrics(
                endpoint=getattr(func, '__name__', 'unknown'),
                method='FUNCTION',
                response_time=end_time - start_time,
                memory_usage=end_memory - start_memory,
                cpu_usage=0.0,  # Would need psutil for accurate CPU measurement
                timestamp=datetime.now(),
                status_code=status_code
            )
            
            # Get global performance monitor instance
            monitor = getattr(performance_monitor, 'monitor', None)
            if monitor:
                monitor.record_metric(metric)
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        """
        Sync Wrapper
        
        
        Example:
            TBD: Add usage example
        """
        start_time = time.time()
        start_memory = _get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            status_code = 200
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            end_time = time.time()
            end_memory = _get_memory_usage()
            
            # Record performance metric
            metric = PerformanceMetrics(
                endpoint=getattr(func, '__name__', 'unknown'),
                method='FUNCTION',
                response_time=end_time - start_time,
                memory_usage=end_memory - start_memory,
                cpu_usage=0.0,
                timestamp=datetime.now(),
                status_code=status_code
            )
            
            # Get global performance monitor instance
            monitor = getattr(performance_monitor, 'monitor', None)
            if monitor:
                monitor.record_metric(metric)
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        """
        Decorator
        
        
        Args:
            func: Description of func
    
        Example:
            TBD: Add usage example
        """
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(func.__name__, args, kwargs, key_prefix)
            
            # Try to get from cache
            cache = getattr(cache_result, 'cache', None)
            if cache:
                cached_result = await cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            if cache:
                await cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """
            Sync Wrapper
            
            
            Example:
                TBD: Add usage example
            """
            # Generate cache key
            cache_key = _generate_cache_key(func.__name__, args, kwargs, key_prefix)
            
            # Try to get from cache
            cache = getattr(cache_result, 'cache', None)
            if cache:
                # For sync functions, we need to run async cache operations
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    cached_result = loop.run_until_complete(cache.get(cache_key))
                    if cached_result is not None:
                        logger.debug(f"Cache hit for {cache_key}")
                        return cached_result
                finally:
                    loop.close()
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            if cache:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(cache.set(cache_key, result, ttl))
                    logger.debug(f"Cached result for {cache_key}")
                finally:
                    loop.close()
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def _get_memory_usage() -> float:
    """Get current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convert to MB
    except ImportError:
        return 0.0

def _generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """Generate cache key from function name and arguments"""
    # Create a hash of the arguments
    args_str = str(args) + str(sorted(kwargs.items()))
    args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
    
    key = f"{prefix}{func_name}:{args_hash}"
    return key

class PerformanceOptimizer:
    """Main performance optimization class"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.db_pool = None
        self.cache = None
        self.monitor = PerformanceMonitor()
        self.query_optimizer = QueryOptimizer()
        
        # Set global instances for decorators
        performance_monitor.monitor = self.monitor
        cache_result.cache = self.cache
    
    async def initialize(self, 
                        db_config: Dict[str, Any] = None,
                        cache_config: Dict[str, Any] = None):
        """Initialize performance optimization components"""
        try:
            # Initialize database pool
            if db_config:
                self.db_pool = DatabaseConnectionPool(**db_config)
            
            # Initialize cache
            if cache_config:
                self.cache = RedisCache(**cache_config)
                cache_result.cache = self.cache
            
            logger.info("Performance optimization components initialized")
        except Exception as e:
            logger.error(f"Failed to initialize performance optimization: {e}")
            raise
    
    async def optimize_database_queries(self, table_name: str, columns: List[str]):
        """Optimize database queries for a table"""
        try:
            suggestions = self.query_optimizer.create_index_suggestions(table_name, columns)
            
            if self.db_pool:
                conn = self.db_pool.get_connection()
                try:
                    cursor = conn.cursor()
                    for suggestion in suggestions:
                        cursor.execute(suggestion)
                    conn.commit()
                    logger.info(f"Database optimization applied for table {table_name}")
                finally:
                    self.db_pool.return_connection(conn)
            
            return suggestions
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return []
    
    async def warm_up_cache(self, endpoints: List[str]):
        """Warm up cache with frequently accessed data"""
        if not self.cache:
            return
        
        try:
            for endpoint in endpoints:
                # This would typically make requests to warm up the cache
                logger.info(f"Warming up cache for endpoint: {endpoint}")
        except Exception as e:
            logger.error(f"Cache warm-up failed: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            "monitor": self.monitor.get_performance_summary(),
            "cache_status": "active" if self.cache else "inactive",
            "db_pool_status": "active" if self.db_pool else "inactive",
            "optimization_suggestions": self._get_optimization_suggestions()
        }
    
    def _get_optimization_suggestions(self) -> List[str]:
        """Get performance optimization suggestions"""
        suggestions = []
        
        summary = self.monitor.get_performance_summary()
        
        if summary.get("average_response_time", 0) > 1.0:
            suggestions.append("Consider implementing more aggressive caching")
        
        if summary.get("cache_hit_rate", 0) < 50:
            suggestions.append("Cache hit rate is low - review cache keys and TTL")
        
        if summary.get("success_rate", 100) < 95:
            suggestions.append("Error rate is high - investigate failing requests")
        
        return suggestions

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

# Convenience functions
async def init_performance_optimization(db_config: Dict[str, Any] = None, 
                                      cache_config: Dict[str, Any] = None):
    """Initialize performance optimization"""
    await performance_optimizer.initialize(db_config, cache_config)

def get_performance_report() -> Dict[str, Any]:
    """Get performance report"""
    return performance_optimizer.get_performance_report()

async def optimize_database(table_name: str, columns: List[str]):
    """Optimize database for table"""
    return await performance_optimizer.optimize_database_queries(table_name, columns)
