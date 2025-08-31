"""
Queue Metrics Collection for Nexus Platform

Implements comprehensive queue monitoring and metrics collection.
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of metrics."""
    QUEUE_SIZE = "queue_size"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"

@dataclass
class QueueMetric:
    """Individual metric data point."""
    id: str
    queue_name: str
    metric_type: MetricType
    value: float
    timestamp: float

@dataclass
class QueueStats:
    """Queue statistics summary."""
    queue_name: str
    current_size: int
    avg_throughput: float
    avg_latency: float
    error_rate: float
    health_score: float

class QueueMetricsCollector:
    """Collects and manages queue metrics."""

    def __init__(self, retention_hours: int = 24):
        """Initializes the QueueMetricsCollector."""
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.queue_stats: Dict[str, QueueStats] = {}
        self.is_collecting = False
        logger.info("Queue Metrics Collector initialized")

    def record_metric(self, queue_name: str, metric_type: MetricType, value: float):
        """Records a new metric."""
        metric = QueueMetric(
            id=str(uuid.uuid4()),
            queue_name=queue_name,
            metric_type=metric_type,
            value=value,
            timestamp=time.time(),
        )
        key = f"{queue_name}_{metric_type.value}"
        self.metrics[key].append(metric)
        self._update_queue_stats(queue_name, metric_type, value)

    def _update_queue_stats(self, queue_name: str, metric_type: MetricType, value: float):
        """Updates the statistics for a given queue."""
        if queue_name not in self.queue_stats:
            self.queue_stats[queue_name] = QueueStats(
                queue_name=queue_name,
                current_size=0,
                avg_throughput=0.0,
                avg_latency=0.0,
                error_rate=0.0,
                health_score=100.0,
            )
        
        stats = self.queue_stats[queue_name]
        
        if metric_type == MetricType.QUEUE_SIZE:
            stats.current_size = int(value)
        elif metric_type == MetricType.THROUGHPUT:
            stats.avg_throughput = (stats.avg_throughput * 0.9) + (value * 0.1)
        elif metric_type == MetricType.LATENCY:
            stats.avg_latency = (stats.avg_latency * 0.9) + (value * 0.1)
        elif metric_type == MetricType.ERROR_RATE:
            stats.error_rate = value

        stats.health_score = self.calculate_queue_health_score(queue_name)

    def calculate_queue_health_score(self, queue_name: str) -> float:
        """Calculates a health score for a queue (0-100)."""
        stats = self.queue_stats.get(queue_name)
        if not stats:
            return 0.0

        size_score = max(0, 100 - (stats.current_size / 1000) * 100)
        latency_score = max(0, 100 - (stats.avg_latency / 1000) * 100)
        error_score = max(0, 100 - stats.error_rate * 100)

        health_score = (size_score * 0.4 + latency_score * 0.4 + error_score * 0.2)
        return min(100.0, max(0.0, health_score))

    def get_queue_stats(self, queue_name: str) -> Optional[QueueStats]:
        """Gets the current statistics for a queue."""
        return self.queue_stats.get(queue_name)

def test_queue_metrics():
    """Tests the Queue Metrics Collector."""
    logging.basicConfig(level=logging.INFO)
    print("🧪 Testing Queue Metrics Collector")
    collector = QueueMetricsCollector()
    collector.record_metric("test_queue", MetricType.QUEUE_SIZE, 150)
    collector.record_metric("test_queue", MetricType.LATENCY, 45.2)
    collector.record_metric("test_queue", MetricType.ERROR_RATE, 0.02)
    
    stats = collector.get_queue_stats("test_queue")
    if stats:
        print(f"  Queue: {stats.queue_name}")
        print(f"  Health Score: {stats.health_score:.1f}/100")

if __name__ == "__main__":
    test_queue_metrics()
