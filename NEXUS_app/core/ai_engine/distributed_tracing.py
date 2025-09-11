#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔍 Frenly AI Distributed Tracing System
OpenTelemetry integration for request tracing and analysis
"""

import asyncio
import logging
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class TraceStatus(Enum):
    """Trace status enumeration"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SpanType(Enum):
    """Span type enumeration"""
    REQUEST = "request"
    RESPONSE = "response"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL = "external"
    INTERNAL = "internal"

@dataclass
class Span:
    """Trace span definition"""
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    name: str
    span_type: SpanType
    start_time: str
    end_time: Optional[str]
    duration: Optional[float]
    status: TraceStatus
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Trace:
    """Trace definition"""
    trace_id: str
    root_span_id: str
    start_time: str
    end_time: Optional[str]
    duration: Optional[float]
    status: TraceStatus
    spans: List[Span] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DistributedTracing:
    """Distributed tracing system with OpenTelemetry integration"""
    
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
        
        # Trace storage
        self.active_traces: Dict[str, Trace] = {}
        self.completed_traces: List[Trace] = []
        
        # Tracing configuration
        self.trace_retention = 3600  # 1 hour
        self.max_traces = 10000
        self.sampling_rate = 1.0  # 100% sampling
        
        logger.info("✅ Distributed Tracing initialized")
    
    async def start(self):
        """Start the distributed tracing system"""
        self.running = True
        logger.info("🚀 Starting Distributed Tracing...")
        
        # Start background tasks
        asyncio.create_task(self._process_traces())
        asyncio.create_task(self._cleanup_old_traces())
        
        logger.info("✅ Distributed Tracing started")
    
    async def stop(self):
        """Stop the distributed tracing system"""
        self.running = False
        logger.info("🛑 Stopping Distributed Tracing...")
        
        # Complete all active traces
        for trace in self.active_traces.values():
            await self._complete_trace(trace.trace_id)
        
        logger.info("✅ Distributed Tracing stopped")
    
    async def start_trace(self, trace_name: str, tags: Optional[Dict[str, str]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new trace"""
        try:
            trace_id = str(uuid.uuid4())
            root_span_id = str(uuid.uuid4())
            
            trace = Trace(
                trace_id=trace_id,
                root_span_id=root_span_id,
                start_time=datetime.now().isoformat(),
                status=TraceStatus.STARTED,
                tags=tags or {},
                metadata=metadata or {}
            )
            
            # Create root span
            root_span = Span(
                span_id=root_span_id,
                trace_id=trace_id,
                parent_span_id=None,
                name=trace_name,
                span_type=SpanType.REQUEST,
                start_time=datetime.now().isoformat(),
                status=TraceStatus.STARTED
            )
            
            trace.spans.append(root_span)
            self.active_traces[trace_id] = trace
            
            logger.debug(f"Trace started: {trace_id}")
            return trace_id
            
        except Exception as e:
            logger.error(f"❌ Error starting trace: {e}")
            return None
    
    async def start_span(self, trace_id: str, span_name: str, span_type: SpanType,
                        parent_span_id: Optional[str] = None,
                        tags: Optional[Dict[str, str]] = None) -> str:
        """Start a new span within a trace"""
        try:
            if trace_id not in self.active_traces:
                logger.warning(f"Trace not found: {trace_id}")
                return None
            
            span_id = str(uuid.uuid4())
            
            span = Span(
                span_id=span_id,
                trace_id=trace_id,
                parent_span_id=parent_span_id,
                name=span_name,
                span_type=span_type,
                start_time=datetime.now().isoformat(),
                status=TraceStatus.STARTED,
                tags=tags or {}
            )
            
            self.active_traces[trace_id].spans.append(span)
            
            logger.debug(f"Span started: {span_id} in trace {trace_id}")
            return span_id
            
        except Exception as e:
            logger.error(f"❌ Error starting span: {e}")
            return None
    
    async def end_span(self, trace_id: str, span_id: str, status: TraceStatus = TraceStatus.COMPLETED,
                      logs: Optional[List[Dict[str, Any]]] = None,
                      metadata: Optional[Dict[str, Any]] = None):
        """End a span"""
        try:
            if trace_id not in self.active_traces:
                logger.warning(f"Trace not found: {trace_id}")
                return
            
            trace = self.active_traces[trace_id]
            span = next((s for s in trace.spans if s.span_id == span_id), None)
            
            if not span:
                logger.warning(f"Span not found: {span_id}")
                return
            
            # Update span
            span.end_time = datetime.now().isoformat()
            span.duration = (datetime.fromisoformat(span.end_time) - 
                           datetime.fromisoformat(span.start_time)).total_seconds()
            span.status = status
            span.logs.extend(logs or [])
            span.metadata.update(metadata or {})
            
            logger.debug(f"Span ended: {span_id} in trace {trace_id}")
            
        except Exception as e:
            logger.error(f"❌ Error ending span: {e}")
    
    async def add_span_log(self, trace_id: str, span_id: str, message: str,
                          level: str = "info", metadata: Optional[Dict[str, Any]] = None):
        """Add a log entry to a span"""
        try:
            if trace_id not in self.active_traces:
                return
            
            trace = self.active_traces[trace_id]
            span = next((s for s in trace.spans if s.span_id == span_id), None)
            
            if not span:
                return
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message,
                "metadata": metadata or {}
            }
            
            span.logs.append(log_entry)
            
        except Exception as e:
            logger.error(f"❌ Error adding span log: {e}")
    
    async def add_span_tag(self, trace_id: str, span_id: str, key: str, value: str):
        """Add a tag to a span"""
        try:
            if trace_id not in self.active_traces:
                return
            
            trace = self.active_traces[trace_id]
            span = next((s for s in trace.spans if s.span_id == span_id), None)
            
            if not span:
                return
            
            span.tags[key] = value
            
        except Exception as e:
            logger.error(f"❌ Error adding span tag: {e}")
    
    async def complete_trace(self, trace_id: str, status: TraceStatus = TraceStatus.COMPLETED):
        """Complete a trace"""
        try:
            if trace_id not in self.active_traces:
                logger.warning(f"Trace not found: {trace_id}")
                return
            
            await self._complete_trace(trace_id, status)
            
        except Exception as e:
            logger.error(f"❌ Error completing trace: {e}")
    
    async def _complete_trace(self, trace_id: str, status: TraceStatus = TraceStatus.COMPLETED):
        """Internal method to complete a trace"""
        try:
            trace = self.active_traces[trace_id]
            
            # Update trace
            trace.end_time = datetime.now().isoformat()
            trace.duration = (datetime.fromisoformat(trace.end_time) - 
                            datetime.fromisoformat(trace.start_time)).total_seconds()
            trace.status = status
            
            # Move to completed traces
            self.completed_traces.append(trace)
            del self.active_traces[trace_id]
            
            # Keep only recent completed traces
            if len(self.completed_traces) > self.max_traces:
                self.completed_traces = self.completed_traces[-self.max_traces:]
            
            logger.debug(f"Trace completed: {trace_id}")
            
        except Exception as e:
            logger.error(f"❌ Error completing trace internally: {e}")
    
    async def get_trace(self, trace_id: str) -> Optional[Trace]:
        try:
            # Check active traces
            if trace_id in self.active_traces:
                return self.active_traces[trace_id]
            
            # Check completed traces
            for trace in self.completed_traces:
                if trace.trace_id == trace_id:
                    return trace
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting trace: {e}")
            return None
    
    async def get_traces(self, limit: int = 100, status: Optional[TraceStatus] = None) -> List[Trace]:
        """Get traces with optional filtering"""
        try:
            traces = []
            
            # Add active traces
            traces.extend(self.active_traces.values())
            
            # Add completed traces
            traces.extend(self.completed_traces)
            
            # Filter by status
            if status:
                traces = [t for t in traces if t.status == status]
            
            # Sort by start time (newest first)
            traces.sort(key=lambda t: t.start_time, reverse=True)
            
            return traces[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting traces: {e}")
            return []
    
    async def get_trace_analytics(self) -> Dict[str, Any]:
        """Get trace analytics and insights"""
        try:
            all_traces = list(self.active_traces.values()) + self.completed_traces
            
            if not all_traces:
                return {"message": "No traces available"}
            
            # Calculate metrics
            total_traces = len(all_traces)
            completed_traces = len([t for t in all_traces if t.status == TraceStatus.COMPLETED])
            failed_traces = len([t for t in all_traces if t.status == TraceStatus.FAILED])
            
            success_rate = completed_traces / total_traces if total_traces > 0 else 0
            
            # Calculate duration statistics
            durations = [t.duration for t in all_traces if t.duration is not None]
            avg_duration = sum(durations) / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            min_duration = min(durations) if durations else 0
            
            # Calculate span statistics
            total_spans = sum(len(t.spans) for t in all_traces)
            avg_spans_per_trace = total_spans / total_traces if total_traces > 0 else 0
            
            # Find slowest traces
            slowest_traces = sorted(
                [t for t in all_traces if t.duration is not None],
                key=lambda t: t.duration,
                reverse=True
            )[:5]
            
            # Find most common span types
            span_types = {}
            for trace in all_traces:
                for span in trace.spans:
                    span_type = span.span_type.value
                    span_types[span_type] = span_types.get(span_type, 0) + 1
            
            return {
                "total_traces": total_traces,
                "completed_traces": completed_traces,
                "failed_traces": failed_traces,
                "success_rate": success_rate,
                "duration_stats": {
                    "average": avg_duration,
                    "maximum": max_duration,
                    "minimum": min_duration
                },
                "span_stats": {
                    "total_spans": total_spans,
                    "avg_spans_per_trace": avg_spans_per_trace
                },
                "slowest_traces": [
                    {
                        "trace_id": t.trace_id,
                        "duration": t.duration,
                        "status": t.status.value
                    }
                    for t in slowest_traces
                ],
                "span_type_distribution": span_types,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting trace analytics: {e}")
            return {"error": str(e)}
    
    async def get_performance_insights(self) -> Dict[str, Any]:
        """Get performance insights from traces"""
        try:
            all_traces = list(self.active_traces.values()) + self.completed_traces
            completed_traces = [t for t in all_traces if t.status == TraceStatus.COMPLETED and t.duration is not None]
            
            if not completed_traces:
                return {"message": "No completed traces available"}
            
            # Performance analysis
            durations = [t.duration for t in completed_traces]
            avg_duration = sum(durations) / len(durations)
            
            # Identify performance bottlenecks
            slow_traces = [t for t in completed_traces if t.duration > avg_duration * 2]
            
            # Analyze span performance
            span_performance = {}
            for trace in completed_traces:
                for span in trace.spans:
                    if span.duration is not None:
                        span_name = span.name
                        if span_name not in span_performance:
                            span_performance[span_name] = []
                        span_performance[span_name].append(span.duration)
            
            # Calculate average duration per span type
            span_avg_durations = {
                name: sum(durations) / len(durations)
                for name, durations in span_performance.items()
            }
            
            # Find slowest spans
            slowest_spans = sorted(
                span_avg_durations.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                "overall_performance": {
                    "avg_trace_duration": avg_duration,
                    "total_traces_analyzed": len(completed_traces)
                },
                "bottlenecks": {
                    "slow_traces_count": len(slow_traces),
                    "slow_traces_percentage": len(slow_traces) / len(completed_traces) * 100
                },
                "span_performance": {
                    "slowest_spans": [
                        {"span_name": name, "avg_duration": duration}
                        for name, duration in slowest_spans
                    ]
                },
                "recommendations": await self._generate_performance_recommendations(span_avg_durations),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting performance insights: {e}")
            return {"error": str(e)}
    
    async def _generate_performance_recommendations(self, span_durations: Dict[str, float]) -> List[str]:
        """Generate performance recommendations based on span analysis"""
        recommendations = []
        
        # Find spans that are significantly slower than average
        if span_durations:
            avg_span_duration = sum(span_durations.values()) / len(span_durations)
            
            for span_name, duration in span_durations.items():
                if duration > avg_span_duration * 2:
                    recommendations.append(f"Consider optimizing span '{span_name}' - it's {duration/avg_span_duration:.1f}x slower than average")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Performance looks good! No significant bottlenecks detected.")
        
        return recommendations
    
    async def _process_traces(self):
        """Process traces for analysis"""
        while self.running:
            try:
                # Process completed traces
                if self.completed_traces:
                    # Store traces in Redis for persistence
                    await self._store_traces()
                
                await asyncio.sleep(30)  # Process every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error processing traces: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_traces(self):
        """Clean up old traces"""
        while self.running:
            try:
                cutoff_time = datetime.now() - timedelta(seconds=self.trace_retention)
                
                # Clean up completed traces
                old_traces = [
                    t for t in self.completed_traces
                    if datetime.fromisoformat(t.start_time) < cutoff_time
                ]
                
                for trace in old_traces:
                    self.completed_traces.remove(trace)
                
                if old_traces:
                    logger.info(f"Cleaned up {len(old_traces)} old traces")
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up traces: {e}")
                await asyncio.sleep(60)
    
    async def _store_traces(self):
        """Store traces in Redis"""
        try:
            if not self.redis_client:
                return
            
            # Store recent completed traces
            recent_traces = [
                {
                    "trace_id": t.trace_id,
                    "root_span_id": t.root_span_id,
                    "start_time": t.start_time,
                    "end_time": t.end_time,
                    "duration": t.duration,
                    "status": t.status.value,
                    "spans": [
                        {
                            "span_id": s.span_id,
                            "trace_id": s.trace_id,
                            "parent_span_id": s.parent_span_id,
                            "name": s.name,
                            "span_type": s.span_type.value,
                            "start_time": s.start_time,
                            "end_time": s.end_time,
                            "duration": s.duration,
                            "status": s.status.value,
                            "tags": s.tags,
                            "logs": s.logs,
                            "metadata": s.metadata
                        }
                        for s in t.spans
                    ],
                    "tags": t.tags,
                    "metadata": t.metadata
                }
                for t in self.completed_traces[-100:]  # Last 100 traces
            ]
            
            self.redis_client.setex(
                "frenly_traces",
                3600,  # 1 hour TTL
                json.dumps(recent_traces, default=str)
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing traces: {e}")

# Global distributed tracing instance
distributed_tracing = DistributedTracing()
