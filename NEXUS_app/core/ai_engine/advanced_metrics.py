#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📊 Frenly AI Advanced Metrics Collection
Comprehensive metrics collection and analytics for AI service
"""

import asyncio
import logging
import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    CUSTOM = "custom"

class MetricCategory(Enum):
    """Metric category enumeration"""
    BUSINESS = "business"
    TECHNICAL = "technical"
    USER = "user"
    SYSTEM = "system"
    AGENT = "agent"
    WORKFLOW = "workflow"

@dataclass
class MetricPoint:
    """Metric data point"""
    name: str
    value: float
    metric_type: MetricType
    category: MetricCategory
    timestamp: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BusinessMetric:
    """Business metric definition"""
    name: str
    description: str
    value: float
    target: float
    unit: str
    trend: str
    timestamp: str

@dataclass
class AgentPerformance:
    """Agent performance metrics"""
    agent_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    avg_confidence: float
    user_satisfaction: float
    throughput: float
    error_rate: float
    timestamp: str

class AdvancedMetricsCollector:
    """Advanced metrics collection and analytics system"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # Metrics storage
        self.metrics: List[MetricPoint] = []
        self.business_metrics: Dict[str, BusinessMetric] = {}
        self.agent_performance: Dict[str, AgentPerformance] = {}
        
        # Metrics configuration
        self.metrics_retention = 86400  # 24 hours
        self.aggregation_interval = 300  # 5 minutes
        self.alert_thresholds = {
            "error_rate": 0.1,
            "response_time": 5.0,
            "throughput": 10.0,
            "user_satisfaction": 0.7
        }
        
        logger.info("✅ Advanced Metrics Collector initialized")
    
    async def start(self):
        """Start the metrics collector"""
        self.running = True
        logger.info("🚀 Starting Advanced Metrics Collector...")
        
        # Start background tasks
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._collect_business_metrics())
        asyncio.create_task(self._collect_agent_metrics())
        asyncio.create_task(self._aggregate_metrics())
        asyncio.create_task(self._cleanup_old_metrics())
        
        logger.info("✅ Advanced Metrics Collector started")
    
    async def stop(self):
        """Stop the metrics collector"""
        self.running = False
        logger.info("🛑 Stopping Advanced Metrics Collector...")
        
        # Save final metrics
        await self._save_metrics()
        
        logger.info("✅ Advanced Metrics Collector stopped")
    
    async def record_metric(self, name: str, value: float, metric_type: MetricType,
                          category: MetricCategory, tags: Optional[Dict[str, str]] = None,
                          metadata: Optional[Dict[str, Any]] = None):
        """Record a metric point"""
        try:
            metric_point = MetricPoint(
                name=name,
                value=value,
                metric_type=metric_type,
                category=category,
                timestamp=datetime.now().isoformat(),
                tags=tags or {},
                metadata=metadata or {}
            )
            
            self.metrics.append(metric_point)
            
            # Keep only recent metrics
            cutoff_time = datetime.now() - timedelta(seconds=self.metrics_retention)
            self.metrics = [
                m for m in self.metrics 
                if datetime.fromisoformat(m.timestamp) > cutoff_time
            ]
            
            logger.debug(f"Metric recorded: {name} = {value}")
            
        except Exception as e:
            logger.error(f"❌ Error recording metric {name}: {e}")
    
    async def record_business_metric(self, name: str, value: float, target: float,
                                   unit: str, description: str):
        """Record business metric"""
        try:
            # Calculate trend
            previous_value = self.business_metrics.get(name, BusinessMetric(
                name=name, description=description, value=0, target=target,
                unit=unit, trend="stable", timestamp=datetime.now().isoformat()
            )).value
            
            if value > previous_value * 1.05:
                trend = "increasing"
            elif value < previous_value * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
            
            business_metric = BusinessMetric(
                name=name,
                description=description,
                value=value,
                target=target,
                unit=unit,
                trend=trend,
                timestamp=datetime.now().isoformat()
            )
            
            self.business_metrics[name] = business_metric
            
            logger.debug(f"Business metric recorded: {name} = {value} {unit}")
            
        except Exception as e:
            logger.error(f"❌ Error recording business metric {name}: {e}")
    
    async def record_agent_performance(self, agent_id: str, total_requests: int,
                                     successful_requests: int, failed_requests: int,
                                     avg_response_time: float, avg_confidence: float,
                                     user_satisfaction: float):
        """Record agent performance metrics"""
        try:
            throughput = total_requests / 3600  # requests per hour
            error_rate = failed_requests / total_requests if total_requests > 0 else 0
            
            performance = AgentPerformance(
                agent_id=agent_id,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                avg_response_time=avg_response_time,
                avg_confidence=avg_confidence,
                user_satisfaction=user_satisfaction,
                throughput=throughput,
                error_rate=error_rate,
                timestamp=datetime.now().isoformat()
            )
            
            self.agent_performance[agent_id] = performance
            
            logger.debug(f"Agent performance recorded: {agent_id}")
            
        except Exception as e:
            logger.error(f"❌ Error recording agent performance: {e}")
    
    async def get_metrics_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive metrics dashboard"""
        try:
            # Calculate system metrics
            system_metrics = await self._calculate_system_metrics()
            
            # Calculate business metrics
            business_metrics = await self._calculate_business_metrics()
            
            # Calculate agent metrics
            agent_metrics = await self._calculate_agent_metrics()
            
            # Calculate workflow metrics
            workflow_metrics = await self._calculate_workflow_metrics()
            
            # Calculate user metrics
            user_metrics = await self._calculate_user_metrics()
            
            return {
                "system_metrics": system_metrics,
                "business_metrics": business_metrics,
                "agent_metrics": agent_metrics,
                "workflow_metrics": workflow_metrics,
                "user_metrics": user_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting metrics dashboard: {e}")
            return {"error": str(e)}
    
    async def get_agent_analytics(self, agent_id: str) -> Dict[str, Any]:
        try:
            if agent_id not in self.agent_performance:
                return {"error": "Agent not found"}
            
            performance = self.agent_performance[agent_id]
            
            # Get historical data
            agent_metrics = [m for m in self.metrics 
                           if m.tags.get("agent_id") == agent_id]
            
            # Calculate trends
            recent_metrics = [m for m in agent_metrics 
                            if datetime.fromisoformat(m.timestamp) > 
                            datetime.now() - timedelta(hours=1)]
            
            # Performance analysis
            performance_analysis = {
                "current_performance": {
                    "total_requests": performance.total_requests,
                    "success_rate": performance.successful_requests / performance.total_requests,
                    "error_rate": performance.error_rate,
                    "avg_response_time": performance.avg_response_time,
                    "avg_confidence": performance.avg_confidence,
                    "user_satisfaction": performance.user_satisfaction,
                    "throughput": performance.throughput
                },
                "trends": {
                    "performance_trend": "improving" if performance.avg_confidence > 0.8 else "stable",
                    "efficiency_trend": "improving" if performance.avg_response_time < 3.0 else "stable",
                    "reliability_trend": "improving" if performance.error_rate < 0.05 else "stable"
                },
                "recommendations": await self._generate_agent_recommendations(performance),
                "timestamp": datetime.now().isoformat()
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"❌ Error getting agent analytics: {e}")
            return {"error": str(e)}
    
    async def get_business_intelligence(self) -> Dict[str, Any]:
        """Get business intelligence insights"""
        try:
            # Calculate KPIs
            total_requests = sum(p.total_requests for p in self.agent_performance.values())
            total_successful = sum(p.successful_requests for p in self.agent_performance.values())
            overall_success_rate = total_successful / total_requests if total_requests > 0 else 0
            
            revenue_per_request = 0.01  # $0.01 per request
            total_revenue = total_requests * revenue_per_request
            
            # Calculate efficiency metrics
            avg_response_time = np.mean([p.avg_response_time for p in self.agent_performance.values()])
            avg_user_satisfaction = np.mean([p.user_satisfaction for p in self.agent_performance.values()])
            
            # Calculate growth metrics
            recent_requests = sum(1 for m in self.metrics 
                                if m.name == "requests_total" and 
                                datetime.fromisoformat(m.timestamp) > 
                                datetime.now() - timedelta(hours=24))
            
            return {
                "kpis": {
                    "total_requests": total_requests,
                    "success_rate": overall_success_rate,
                    "total_revenue": total_revenue,
                    "avg_response_time": avg_response_time,
                    "user_satisfaction": avg_user_satisfaction
                },
                "growth_metrics": {
                    "requests_last_24h": recent_requests,
                    "growth_rate": "calculating...",  # Would need historical data
                    "trend": "stable"
                },
                "efficiency_metrics": {
                    "cost_per_request": revenue_per_request,
                    "revenue_per_hour": total_revenue / 24,
                    "efficiency_score": min(1.0, overall_success_rate * avg_user_satisfaction)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting business intelligence: {e}")
            return {"error": str(e)}
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        while self.running:
            try:
                import psutil
                
                # CPU usage
                cpu_usage = psutil.cpu_percent(interval=1)
                await self.record_metric(
                    "system_cpu_usage", cpu_usage, MetricType.GAUGE, MetricCategory.SYSTEM
                )
                
                # Memory usage
                memory = psutil.virtual_memory()
                await self.record_metric(
                    "system_memory_usage", memory.percent, MetricType.GAUGE, MetricCategory.SYSTEM
                )
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_usage = (disk.used / disk.total) * 100
                await self.record_metric(
                    "system_disk_usage", disk_usage, MetricType.GAUGE, MetricCategory.SYSTEM
                )
                
                # Network I/O
                network = psutil.net_io_counters()
                await self.record_metric(
                    "system_network_bytes_sent", network.bytes_sent, MetricType.COUNTER, MetricCategory.SYSTEM
                )
                await self.record_metric(
                    "system_network_bytes_recv", network.bytes_recv, MetricType.COUNTER, MetricCategory.SYSTEM
                )
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"❌ Error collecting system metrics: {e}")
                await asyncio.sleep(60)
    
    async def _collect_business_metrics(self):
        """Collect business-level metrics"""
        while self.running:
            try:
                # Calculate business metrics
                total_requests = sum(p.total_requests for p in self.agent_performance.values())
                total_successful = sum(p.successful_requests for p in self.agent_performance.values())
                success_rate = total_successful / total_requests if total_requests > 0 else 0
                
                # Record business metrics
                await self.record_business_metric(
                    "total_requests", total_requests, 10000, "requests", "Total number of requests processed"
                )
                await self.record_business_metric(
                    "success_rate", success_rate, 0.95, "percentage", "Overall success rate"
                )
                
                revenue = total_requests * 0.01
                await self.record_business_metric(
                    "revenue", revenue, 100, "USD", "Total revenue generated"
                )
                
                await asyncio.sleep(300)  # Collect every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error collecting business metrics: {e}")
                await asyncio.sleep(60)
    
    async def _collect_agent_metrics(self):
        """Collect agent-level metrics"""
        while self.running:
            try:
                # This would typically collect metrics from agent managers
                
                for agent_id in ["agent_1", "agent_2", "agent_3"]:
                    if agent_id in self.agent_performance:
                        performance = self.agent_performance[agent_id]
                        
                        await self.record_metric(
                            f"agent_{agent_id}_requests", 
                            performance.total_requests, 
                            MetricType.COUNTER, 
                            MetricCategory.AGENT,
                            {"agent_id": agent_id}
                        )
                        
                        await self.record_metric(
                            f"agent_{agent_id}_response_time", 
                            performance.avg_response_time, 
                            MetricType.TIMER, 
                            MetricCategory.AGENT,
                            {"agent_id": agent_id}
                        )
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"❌ Error collecting agent metrics: {e}")
                await asyncio.sleep(60)
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for reporting"""
        while self.running:
            try:
                # Aggregate metrics by category
                for category in MetricCategory:
                    category_metrics = [m for m in self.metrics if m.category == category]
                    
                    if category_metrics:
                        # Calculate aggregated values
                        total_value = sum(m.value for m in category_metrics)
                        avg_value = total_value / len(category_metrics)
                        max_value = max(m.value for m in category_metrics)
                        min_value = min(m.value for m in category_metrics)
                        
                        # Record aggregated metrics
                        await self.record_metric(
                            f"aggregated_{category.value}_total", 
                            total_value, 
                            MetricType.GAUGE, 
                            category
                        )
                        
                        await self.record_metric(
                            f"aggregated_{category.value}_average", 
                            avg_value, 
                            MetricType.GAUGE, 
                            category
                        )
                
                await asyncio.sleep(self.aggregation_interval)
                
            except Exception as e:
                logger.error(f"❌ Error aggregating metrics: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics"""
        while self.running:
            try:
                cutoff_time = datetime.now() - timedelta(seconds=self.metrics_retention)
                old_count = len(self.metrics)
                
                self.metrics = [
                    m for m in self.metrics 
                    if datetime.fromisoformat(m.timestamp) > cutoff_time
                ]
                
                removed_count = old_count - len(self.metrics)
                if removed_count > 0:
                    logger.info(f"Cleaned up {removed_count} old metrics")
                
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up metrics: {e}")
                await asyncio.sleep(60)
    
    async def _calculate_system_metrics(self) -> Dict[str, Any]:
        """Calculate system metrics"""
        try:
            system_metrics = [m for m in self.metrics if m.category == MetricCategory.SYSTEM]
            
            if not system_metrics:
                return {"message": "No system metrics available"}
            
            # Calculate averages
            cpu_metrics = [m for m in system_metrics if m.name == "system_cpu_usage"]
            memory_metrics = [m for m in system_metrics if m.name == "system_memory_usage"]
            
            avg_cpu = np.mean([m.value for m in cpu_metrics]) if cpu_metrics else 0
            avg_memory = np.mean([m.value for m in memory_metrics]) if memory_metrics else 0
            
            return {
                "cpu_usage": avg_cpu,
                "memory_usage": avg_memory,
                "total_metrics": len(system_metrics)
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating system metrics: {e}")
            return {"error": str(e)}
    
    async def _calculate_business_metrics(self) -> Dict[str, Any]:
        """Calculate business metrics"""
        try:
            return {
                name: {
                    "value": metric.value,
                    "target": metric.target,
                    "unit": metric.unit,
                    "trend": metric.trend,
                    "description": metric.description
                }
                for name, metric in self.business_metrics.items()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating business metrics: {e}")
            return {"error": str(e)}
    
    async def _calculate_agent_metrics(self) -> Dict[str, Any]:
        """Calculate agent metrics"""
        try:
            return {
                agent_id: {
                    "total_requests": perf.total_requests,
                    "success_rate": perf.successful_requests / perf.total_requests,
                    "error_rate": perf.error_rate,
                    "avg_response_time": perf.avg_response_time,
                    "throughput": perf.throughput
                }
                for agent_id, perf in self.agent_performance.items()
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating agent metrics: {e}")
            return {"error": str(e)}
    
    async def _calculate_workflow_metrics(self) -> Dict[str, Any]:
        """Calculate workflow metrics"""
        try:
            workflow_metrics = [m for m in self.metrics if m.category == MetricCategory.WORKFLOW]
            
            return {
                "total_workflows": len(set(m.tags.get("workflow_id", "") for m in workflow_metrics)),
                "total_executions": len(workflow_metrics),
                "avg_execution_time": np.mean([m.value for m in workflow_metrics if m.name == "workflow_execution_time"]) if workflow_metrics else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating workflow metrics: {e}")
            return {"error": str(e)}
    
    async def _calculate_user_metrics(self) -> Dict[str, Any]:
        """Calculate user metrics"""
        try:
            user_metrics = [m for m in self.metrics if m.category == MetricCategory.USER]
            
            return {
                "total_users": len(set(m.tags.get("user_id", "") for m in user_metrics)),
                "total_interactions": len(user_metrics),
                "avg_satisfaction": np.mean([m.value for m in user_metrics if m.name == "user_satisfaction"]) if user_metrics else 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating user metrics: {e}")
            return {"error": str(e)}
    
    async def _generate_agent_recommendations(self, performance: AgentPerformance) -> List[str]:
        """Generate recommendations for agent performance"""
        recommendations = []
        
        if performance.error_rate > 0.1:
            recommendations.append("High error rate detected. Consider improving error handling.")
        
        if performance.avg_response_time > 5.0:
            recommendations.append("Slow response time. Consider performance optimization.")
        
        if performance.user_satisfaction < 0.7:
            recommendations.append("Low user satisfaction. Consider improving response quality.")
        
        if performance.throughput < 10:
            recommendations.append("Low throughput. Consider scaling or optimization.")
        
        return recommendations
    
    async def _save_metrics(self):
        """Save metrics to Redis"""
        try:
            if self.redis_client:
                # Save metrics
                metrics_data = [
                    {
                        "name": m.name,
                        "value": m.value,
                        "metric_type": m.metric_type.value,
                        "category": m.category.value,
                        "timestamp": m.timestamp,
                        "tags": m.tags,
                        "metadata": m.metadata
                    }
                    for m in self.metrics
                ]
                
                self.redis_client.setex(
                    "frenly_advanced_metrics",
                    3600,  # 1 hour TTL
                    json.dumps(metrics_data, default=str)
                )
                
                # Save business metrics
                business_data = {
                    name: {
                        "name": metric.name,
                        "description": metric.description,
                        "value": metric.value,
                        "target": metric.target,
                        "unit": metric.unit,
                        "trend": metric.trend,
                        "timestamp": metric.timestamp
                    }
                    for name, metric in self.business_metrics.items()
                }
                
                self.redis_client.setex(
                    "frenly_business_metrics",
                    3600,  # 1 hour TTL
                    json.dumps(business_data, default=str)
                )
            
        except Exception as e:
            logger.error(f"❌ Error saving metrics: {e}")

# Global advanced metrics collector instance
advanced_metrics = AdvancedMetricsCollector()
