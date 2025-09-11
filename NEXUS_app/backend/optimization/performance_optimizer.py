#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
⚡ Performance Optimization System for Nexus Platform
Comprehensive performance analysis, optimization, and monitoring
"""

import asyncio
import logging
import time
import psutil
import redis
import asyncpg
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import subprocess
import os
from pathlib import Path
import sqlalchemy
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_io: Dict[str, int]
    network_io: Dict[str, int]
    database_connections: int
    cache_hit_rate: float
    response_time_p95: float
    response_time_p99: float
    requests_per_second: float
    error_rate: float

class PerformanceOptimizer:
    """Comprehensive performance optimization system"""
    
    def __init__(
        """
          Init  
        
        
        Args:
            database_url: Description of database_url
            redis_client: Description of redis_client
            optimization_thresholds: Description of optimization_thresholds
    
        Example:
            TBD: Add usage example
        """
        self,
        database_url: str,
        redis_client: Optional[redis.Redis] = None,
        optimization_thresholds: Optional[Dict[str, float]] = None
    ):
        self.database_url = database_url
        self.redis_client = redis_client
        self.thresholds = optimization_thresholds or {
            "cpu_usage": 0.8,
            "memory_usage": 0.8,
            "response_time_p95": 2.0,
            "response_time_p99": 5.0,
            "error_rate": 0.05,
            "cache_hit_rate": 0.7
        }
        self.metrics_history: List[PerformanceMetrics] = []
        self.optimization_recommendations: List[Dict[str, Any]] = []
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """Comprehensive performance analysis"""
        logger.info("🔍 Starting performance analysis...")
        
        # Collect system metrics
        system_metrics = await self._collect_system_metrics()
        
        # Analyze database performance
        db_metrics = await self._analyze_database_performance()
        
        # Analyze cache performance
        cache_metrics = await self._analyze_cache_performance()
        
        # Analyze application performance
        app_metrics = await self._analyze_application_performance()
        
        # Generate recommendations
        recommendations = await self._generate_optimization_recommendations(
            system_metrics, db_metrics, cache_metrics, app_metrics
        )
        
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": system_metrics,
            "database_metrics": db_metrics,
            "cache_metrics": cache_metrics,
            "application_metrics": app_metrics,
            "recommendations": recommendations,
            "overall_score": self._calculate_performance_score(
                system_metrics, db_metrics, cache_metrics, app_metrics
            )
        }
        
        logger.info(f"Performance analysis completed. Overall score: {analysis_result['overall_score']}/100")
        return analysis_result
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None,
                    "process_usage_percent": process_cpu
                },
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used,
                    "usage_percent": memory.percent,
                    "process_memory_bytes": process_memory.rss,
                    "swap_used_bytes": swap.used,
                    "swap_usage_percent": swap.percent
                },
                "disk": {
                    "total_bytes": disk_usage.total,
                    "used_bytes": disk_usage.used,
                    "free_bytes": disk_usage.free,
                    "usage_percent": (disk_usage.used / disk_usage.total) * 100,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                },
                "network": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv
                }
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    async def _analyze_database_performance(self) -> Dict[str, Any]:
        """Analyze database performance"""
        try:
            # Parse database URL
            db_config = self._parse_database_url()
            
            # Connect to database
            conn = await asyncpg.connect(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )
            
            try:
                # Database size
                db_size = await conn.fetchval("SELECT pg_database_size(current_database())")
                
                # Connection count
                connection_count = await conn.fetchval("""
                    SELECT count(*) FROM pg_stat_activity 
                    WHERE state = 'active'
                """)
                
                # Slow queries
                slow_queries = await conn.fetch("""
                    SELECT query, mean_time, calls, total_time
                    FROM pg_stat_statements
                    WHERE mean_time > 1000  -- Queries taking more than 1 second
                    ORDER BY mean_time DESC
                    LIMIT 10
                """)
                
                # Table statistics
                table_stats = await conn.fetch("""
                    SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del,
                           n_live_tup, n_dead_tup, last_vacuum, last_autovacuum,
                           last_analyze, last_autoanalyze
                    FROM pg_stat_user_tables
                    ORDER BY n_live_tup DESC
                """)
                
                # Index usage
                index_usage = await conn.fetch("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch,
                           idx_scan, idx_tup_read/idx_scan as avg_tuples_per_scan
                    FROM pg_stat_user_indexes
                    WHERE idx_scan > 0
                    ORDER BY idx_tup_read DESC
                """)
                
                # Lock information
                locks = await conn.fetch("""
                    SELECT mode, count(*) as count
                    FROM pg_locks
                    GROUP BY mode
                """)
                
                return {
                    "database_size_bytes": db_size,
                    "active_connections": connection_count,
                    "slow_queries": [dict(q) for q in slow_queries],
                    "table_statistics": [dict(t) for t in table_stats],
                    "index_usage": [dict(i) for i in index_usage],
                    "locks": [dict(l) for l in locks]
                }
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error analyzing database performance: {e}")
            return {}
    
    async def _analyze_cache_performance(self) -> Dict[str, Any]:
        """Analyze cache performance"""
        if not self.redis_client:
            return {"error": "Redis client not available"}
        
        try:
            # Get Redis info
            info = self.redis_client.info()
            
            # Calculate cache hit rate
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total_requests = hits + misses
            hit_rate = hits / total_requests if total_requests > 0 else 0
            
            # Memory usage
            used_memory = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            memory_usage_percent = (used_memory / max_memory * 100) if max_memory > 0 else 0
            
            # Connection info
            connected_clients = info.get('connected_clients', 0)
            
            # Key statistics
            total_keys = self.redis_client.dbsize()
            
            return {
                "hit_rate": hit_rate,
                "total_requests": total_requests,
                "hits": hits,
                "misses": misses,
                "memory_usage_bytes": used_memory,
                "memory_usage_percent": memory_usage_percent,
                "connected_clients": connected_clients,
                "total_keys": total_keys,
                "uptime_seconds": info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing cache performance: {e}")
            return {"error": str(e)}
    
    async def _analyze_application_performance(self) -> Dict[str, Any]:
        """Analyze application performance"""
        try:
            # This would typically come from your application metrics
            
            # Get response time metrics from Redis if available
            if self.redis_client:
                response_times = []
                for key in self.redis_client.scan_iter(match="response_time:*"):
                    time_str = self.redis_client.get(key)
                    if time_str:
                        response_times.append(float(time_str))
                
                if response_times:
                    p95 = np.percentile(response_times, 95)
                    p99 = np.percentile(response_times, 99)
                    avg_response_time = np.mean(response_times)
                else:
                    p95 = p99 = avg_response_time = 0
            else:
                p95 = p99 = avg_response_time = 0
            
            return {
                "response_time_p95": p95,
                "response_time_p99": p99,
                "avg_response_time": avg_response_time,
                "requests_per_second": 0,  # Would be calculated from actual metrics
                "error_rate": 0  # Would be calculated from actual metrics
            }
            
        except Exception as e:
            logger.error(f"Error analyzing application performance: {e}")
            return {}
    
    async def _generate_optimization_recommendations(
        self,
        system_metrics: Dict[str, Any],
        db_metrics: Dict[str, Any],
        cache_metrics: Dict[str, Any],
        app_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # CPU optimization
        cpu_usage = system_metrics.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage > self.thresholds["cpu_usage"] * 100:
            recommendations.append({
                "category": "CPU",
                "priority": "high",
                "issue": f"High CPU usage: {cpu_usage:.1f}%",
                "recommendation": "Consider scaling horizontally or optimizing CPU-intensive operations",
                "actions": [
                    "Add more worker processes",
                    "Optimize algorithms with high CPU usage",
                    "Consider using async/await for I/O operations",
                    "Profile code to identify bottlenecks"
                ]
            })
        
        # Memory optimization
        memory_usage = system_metrics.get("memory", {}).get("usage_percent", 0)
        if memory_usage > self.thresholds["memory_usage"] * 100:
            recommendations.append({
                "category": "Memory",
                "priority": "high",
                "issue": f"High memory usage: {memory_usage:.1f}%",
                "recommendation": "Optimize memory usage and consider scaling",
                "actions": [
                    "Implement memory pooling for frequently used objects",
                    "Optimize data structures to reduce memory footprint",
                    "Add more memory or scale horizontally",
                    "Review and optimize data loading patterns"
                ]
            })
        
        # Database optimization
        if db_metrics.get("slow_queries"):
            recommendations.append({
                "category": "Database",
                "priority": "medium",
                "issue": f"Found {len(db_metrics['slow_queries'])} slow queries",
                "recommendation": "Optimize slow database queries",
                "actions": [
                    "Add appropriate indexes",
                    "Rewrite queries for better performance",
                    "Consider query result caching",
                    "Review database schema design"
                ]
            })
        
        # Cache optimization
        hit_rate = cache_metrics.get("hit_rate", 0)
        if hit_rate < self.thresholds["cache_hit_rate"]:
            recommendations.append({
                "category": "Cache",
                "priority": "medium",
                "issue": f"Low cache hit rate: {hit_rate:.2%}",
                "recommendation": "Improve caching strategy",
                "actions": [
                    "Review cache key strategy",
                    "Increase cache TTL for frequently accessed data",
                    "Implement cache warming strategies",
                    "Consider using different cache eviction policies"
                ]
            })
        
        # Response time optimization
        response_time_p95 = app_metrics.get("response_time_p95", 0)
        if response_time_p95 > self.thresholds["response_time_p95"]:
            recommendations.append({
                "category": "Response Time",
                "priority": "high",
                "issue": f"High 95th percentile response time: {response_time_p95:.3f}s",
                "recommendation": "Optimize response times",
                "actions": [
                    "Implement response caching",
                    "Optimize database queries",
                    "Use CDN for static content",
                    "Implement request batching"
                ]
            })
        
        return recommendations
    
    def _calculate_performance_score(
        self,
        system_metrics: Dict[str, Any],
        db_metrics: Dict[str, Any],
        cache_metrics: Dict[str, Any],
        app_metrics: Dict[str, Any]
    ) -> int:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # CPU score
        cpu_usage = system_metrics.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage > 90:
            score -= 30
        elif cpu_usage > 80:
            score -= 20
        elif cpu_usage > 70:
            score -= 10
        
        # Memory score
        memory_usage = system_metrics.get("memory", {}).get("usage_percent", 0)
        if memory_usage > 90:
            score -= 30
        elif memory_usage > 80:
            score -= 20
        elif memory_usage > 70:
            score -= 10
        
        # Response time score
        response_time_p95 = app_metrics.get("response_time_p95", 0)
        if response_time_p95 > 5:
            score -= 25
        elif response_time_p95 > 2:
            score -= 15
        elif response_time_p95 > 1:
            score -= 5
        
        # Cache hit rate score
        hit_rate = cache_metrics.get("hit_rate", 0)
        if hit_rate < 0.5:
            score -= 20
        elif hit_rate < 0.7:
            score -= 10
        
        return max(0, score)
    
    def _parse_database_url(self) -> Dict[str, Any]:
        """Parse database URL into components"""
        url = self.database_url.replace("postgresql://", "")
        
        if "@" in url:
            auth, host_db = url.split("@", 1)
            if ":" in auth:
                user, password = auth.split(":", 1)
            else:
                user, password = auth, ""
        else:
            user, password = "", ""
            host_db = url
        
        if "/" in host_db:
            host_port, database = host_db.split("/", 1)
        else:
            host_port, database = host_db, ""
        
        if ":" in host_port:
            host, port = host_port.split(":", 1)
            port = int(port)
        else:
            host, port = host_port, 5432
        
        return {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }
    
    async def optimize_database(self) -> bool:
        """Optimize database performance"""
        try:
            logger.info("🔧 Optimizing database performance...")
            
            db_config = self._parse_database_url()
            conn = await asyncpg.connect(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )
            
            try:
                # Update statistics
                await conn.execute("ANALYZE")
                logger.info("Updated table statistics")
                
                # Vacuum tables
                await conn.execute("VACUUM ANALYZE")
                logger.info("Vacuumed and analyzed tables")
                
                # Reindex if needed
                await conn.execute("REINDEX DATABASE")
                logger.info("Reindexed database")
                
                return True
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False
    
    async def optimize_cache(self) -> bool:
        """Optimize cache performance"""
        if not self.redis_client:
            return False
        
        try:
            logger.info("🔧 Optimizing cache performance...")
            
            # Clear expired keys
            self.redis_client.eval("return redis.call('del', unpack(redis.call('keys', 'expired:*')))", 0)
            
            # Optimize memory usage
            self.redis_client.memory_purge()
            
            # Set optimal configuration
            self.redis_client.config_set("maxmemory-policy", "allkeys-lru")
            
            logger.info("Cache optimization completed")
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing cache: {e}")
            return False
    
    async def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        analysis = await self.analyze_performance()
        
        report = f"""
# ⚡ Nexus Platform Performance Report
**Generated:** {analysis['timestamp']}
**Overall Score:** {analysis['overall_score']}/100

## 📊 System Metrics
- **CPU Usage:** {analysis['system_metrics'].get('cpu', {}).get('usage_percent', 0):.1f}%
- **Memory Usage:** {analysis['system_metrics'].get('memory', {}).get('usage_percent', 0):.1f}%
- **Disk Usage:** {analysis['system_metrics'].get('disk', {}).get('usage_percent', 0):.1f}%

## 🗄️ Database Metrics
- **Database Size:** {analysis['database_metrics'].get('database_size_bytes', 0) / (1024**3):.2f} GB
- **Active Connections:** {analysis['database_metrics'].get('active_connections', 0)}
- **Slow Queries:** {len(analysis['database_metrics'].get('slow_queries', []))}

## 🚀 Cache Metrics
- **Hit Rate:** {analysis['cache_metrics'].get('hit_rate', 0):.2%}
- **Total Keys:** {analysis['cache_metrics'].get('total_keys', 0)}
- **Memory Usage:** {analysis['cache_metrics'].get('memory_usage_percent', 0):.1f}%

## 📈 Application Metrics
- **95th Percentile Response Time:** {analysis['application_metrics'].get('response_time_p95', 0):.3f}s
- **99th Percentile Response Time:** {analysis['application_metrics'].get('response_time_p99', 0):.3f}s

## 💡 Optimization Recommendations
"""
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            report += f"""
### {i}. {rec['category']} - {rec['priority'].upper()} Priority
**Issue:** {rec['issue']}
**Recommendation:** {rec['recommendation']}

**Actions:**
"""
            for action in rec['actions']:
                report += f"- {action}\n"
        
        return report

# CLI interface
async def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nexus Platform Performance Optimizer")
    parser.add_argument("--database-url", required=True, help="Database URL")
    parser.add_argument("--redis-url", help="Redis URL")
    parser.add_argument("--action", choices=["analyze", "optimize", "report"], default="analyze", help="Action to perform")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    # Initialize Redis client if URL provided
    redis_client = None
    if args.redis_url:
        redis_client = redis.from_url(args.redis_url)
    
    optimizer = PerformanceOptimizer(args.database_url, redis_client)
    
    if args.action == "analyze":
        analysis = await optimizer.analyze_performance()
        print(json.dumps(analysis, indent=2, default=str))
    
    elif args.action == "optimize":
        db_success = await optimizer.optimize_database()
        cache_success = await optimizer.optimize_cache()
        print(f"Database optimization: {'Success' if db_success else 'Failed'}")
        print(f"Cache optimization: {'Success' if cache_success else 'Failed'}")
    
    elif args.action == "report":
        report = await optimizer.generate_performance_report()
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)

if __name__ == "__main__":
    asyncio.run(main())
