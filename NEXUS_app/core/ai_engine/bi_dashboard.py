#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📊 Frenly AI BI Dashboard Integration
Business Intelligence dashboard for Frenly AI analytics
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Chart type enumeration"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"

class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class DashboardType(Enum):
    """Dashboard type enumeration"""
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    CUSTOM = "custom"

@dataclass
class Metric:
    """Metric definition"""
    id: str
    name: str
    description: str
    metric_type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    unit: Optional[str] = None

@dataclass
class Chart:
    """Chart definition"""
    id: str
    title: str
    chart_type: ChartType
    data_source: str
    x_axis: str
    y_axis: str
    filters: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 60  # seconds

@dataclass
class Dashboard:
    """Dashboard definition"""
    id: str
    name: str
    description: str
    dashboard_type: DashboardType
    charts: List[Chart] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    enabled: bool = True

@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    metric_id: str
    condition: str
    threshold: float
    operator: str  # >, <, >=, <=, ==, !=
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_triggered: Optional[str] = None

class BIDashboard:
    """BI Dashboard for Frenly AI"""
    
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
        
        # BI storage
        self.metrics: Dict[str, Metric] = {}
        self.charts: Dict[str, Chart] = {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.alerts: Dict[str, Alert] = {}
        
        # Configuration
        self.metric_retention_days = 30
        self.alert_check_interval = 60  # seconds
        self.chart_refresh_interval = 60  # seconds
        
        logger.info("✅ BI Dashboard initialized")
    
    async def start(self):
        """Start the BI dashboard"""
        self.running = True
        logger.info("🚀 Starting BI Dashboard...")
        
        # Load existing data
        await self._load_bi_data()
        
        # Start background tasks
        asyncio.create_task(self._collect_metrics())
        asyncio.create_task(self._refresh_charts())
        asyncio.create_task(self._check_alerts())
        asyncio.create_task(self._cleanup_old_metrics())
        
        logger.info("✅ BI Dashboard started")
    
    async def stop(self):
        """Stop the BI dashboard"""
        self.running = False
        logger.info("🛑 Stopping BI Dashboard...")
        
        # Save BI data
        await self._save_bi_data()
        
        logger.info("✅ BI Dashboard stopped")
    
    async def create_metric(
        self,
        name: str,
        description: str,
        metric_type: MetricType,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        unit: Optional[str] = None
    ) -> str:
        """Create a new metric"""
        try:
            metric_id = f"metric_{int(time.time())}"
            
            metric = Metric(
                id=metric_id,
                name=name,
                description=description,
                metric_type=metric_type,
                value=value,
                labels=labels or {},
                unit=unit
            )
            
            self.metrics[metric_id] = metric
            
            logger.info(f"Metric created: {metric_id}")
            return metric_id
            
        except Exception as e:
            logger.error(f"❌ Error creating metric: {e}")
            raise
    
    async def update_metric(self, metric_id: str, value: float, labels: Optional[Dict[str, str]] = None) -> bool:
        """Update a metric value"""
        try:
            if metric_id not in self.metrics:
                logger.warning(f"Metric not found: {metric_id}")
                return False
            
            metric = self.metrics[metric_id]
            metric.value = value
            metric.timestamp = datetime.now().isoformat()
            
            if labels:
                metric.labels.update(labels)
            
            logger.debug(f"Metric updated: {metric_id} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating metric {metric_id}: {e}")
            return False
    
    async def get_metric(self, metric_id: str) -> Optional[Metric]:
        """Get metric information"""
        return self.metrics.get(metric_id)
    
    async def list_metrics(self, metric_type: Optional[MetricType] = None) -> List[Metric]:
        """List metrics with optional type filter"""
        metrics = list(self.metrics.values())
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        return metrics
    
    async def create_chart(
        self,
        title: str,
        chart_type: ChartType,
        data_source: str,
        x_axis: str,
        y_axis: str,
        filters: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        refresh_interval: int = 60
    ) -> str:
        """Create a new chart"""
        try:
            chart_id = f"chart_{int(time.time())}"
            
            chart = Chart(
                id=chart_id,
                title=title,
                chart_type=chart_type,
                data_source=data_source,
                x_axis=x_axis,
                y_axis=y_axis,
                filters=filters or {},
                config=config or {},
                refresh_interval=refresh_interval
            )
            
            self.charts[chart_id] = chart
            
            logger.info(f"Chart created: {chart_id}")
            return chart_id
            
        except Exception as e:
            logger.error(f"❌ Error creating chart: {e}")
            raise
    
    async def get_chart(self, chart_id: str) -> Optional[Chart]:
        """Get chart information"""
        return self.charts.get(chart_id)
    
    async def list_charts(self) -> List[Chart]:
        """List all charts"""
        return list(self.charts.values())
    
    async def create_dashboard(
        self,
        name: str,
        description: str,
        dashboard_type: DashboardType,
        charts: Optional[List[str]] = None,
        layout: Optional[Dict[str, Any]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new dashboard"""
        try:
            dashboard_id = f"dashboard_{int(time.time())}"
            
            # Get chart objects
            chart_objects = []
            if charts:
                for chart_id in charts:
                    if chart_id in self.charts:
                        chart_objects.append(self.charts[chart_id])
            
            dashboard = Dashboard(
                id=dashboard_id,
                name=name,
                description=description,
                dashboard_type=dashboard_type,
                charts=chart_objects,
                layout=layout or {},
                filters=filters or {}
            )
            
            self.dashboards[dashboard_id] = dashboard
            
            logger.info(f"Dashboard created: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Error creating dashboard: {e}")
            raise
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard information"""
        return self.dashboards.get(dashboard_id)
    
    async def list_dashboards(self, dashboard_type: Optional[DashboardType] = None) -> List[Dashboard]:
        """List dashboards with optional type filter"""
        dashboards = list(self.dashboards.values())
        
        if dashboard_type:
            dashboards = [d for d in dashboards if d.dashboard_type == dashboard_type]
        
        return dashboards
    
    async def add_chart_to_dashboard(self, dashboard_id: str, chart_id: str) -> bool:
        """Add chart to dashboard"""
        try:
            if dashboard_id not in self.dashboards:
                logger.warning(f"Dashboard not found: {dashboard_id}")
                return False
            
            if chart_id not in self.charts:
                logger.warning(f"Chart not found: {chart_id}")
                return False
            
            dashboard = self.dashboards[dashboard_id]
            chart = self.charts[chart_id]
            
            if chart not in dashboard.charts:
                dashboard.charts.append(chart)
                dashboard.updated_at = datetime.now().isoformat()
                
                logger.info(f"Chart added to dashboard: {chart_id} -> {dashboard_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error adding chart to dashboard: {e}")
            return False
    
    async def create_alert(
        self,
        name: str,
        metric_id: str,
        condition: str,
        threshold: float,
        operator: str = ">"
    ) -> str:
        """Create a new alert"""
        try:
            alert_id = f"alert_{int(time.time())}"
            
            alert = Alert(
                id=alert_id,
                name=name,
                metric_id=metric_id,
                condition=condition,
                threshold=threshold,
                operator=operator
            )
            
            self.alerts[alert_id] = alert
            
            logger.info(f"Alert created: {alert_id}")
            return alert_id
            
        except Exception as e:
            logger.error(f"❌ Error creating alert: {e}")
            raise
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert information"""
        return self.alerts.get(alert_id)
    
    async def list_alerts(self) -> List[Alert]:
        """List all alerts"""
        return list(self.alerts.values())
    
    async def get_chart_data(self, chart_id: str, time_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get chart data"""
        try:
            if chart_id not in self.charts:
                logger.warning(f"Chart not found: {chart_id}")
                return {}
            
            chart = self.charts[chart_id]
            
            # This would query actual data sources
            
            
        except Exception as e:
            logger.error(f"❌ Error getting chart data: {e}")
            return {}
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Get dashboard data"""
        try:
            if dashboard_id not in self.dashboards:
                logger.warning(f"Dashboard not found: {dashboard_id}")
                return {}
            
            dashboard = self.dashboards[dashboard_id]
            
            # Get data for all charts in the dashboard
            charts_data = {}
            for chart in dashboard.charts:
                charts_data[chart.id] = await self.get_chart_data(chart.id)
            
            return {
                "dashboard": {
                    "id": dashboard.id,
                    "name": dashboard.name,
                    "description": dashboard.description,
                    "type": dashboard.dashboard_type.value,
                    "layout": dashboard.layout,
                    "filters": dashboard.filters
                },
                "charts": charts_data
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting dashboard data: {e}")
            return {}
    
    async def get_bi_analytics(self) -> Dict[str, Any]:
        """Get BI analytics"""
        try:
            total_metrics = len(self.metrics)
            total_charts = len(self.charts)
            total_dashboards = len(self.dashboards)
            total_alerts = len(self.alerts)
            
            # Metric type distribution
            metric_type_distribution = {}
            for metric in self.metrics.values():
                metric_type = metric.metric_type.value
                metric_type_distribution[metric_type] = metric_type_distribution.get(metric_type, 0) + 1
            
            # Chart type distribution
            chart_type_distribution = {}
            for chart in self.charts.values():
                chart_type = chart.chart_type.value
                chart_type_distribution[chart_type] = chart_type_distribution.get(chart_type, 0) + 1
            
            # Dashboard type distribution
            dashboard_type_distribution = {}
            for dashboard in self.dashboards.values():
                dashboard_type = dashboard.dashboard_type.value
                dashboard_type_distribution[dashboard_type] = dashboard_type_distribution.get(dashboard_type, 0) + 1
            
            # Active alerts
            active_alerts = len([a for a in self.alerts.values() if a.enabled])
            
            return {
                "total_metrics": total_metrics,
                "total_charts": total_charts,
                "total_dashboards": total_dashboards,
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "metric_type_distribution": metric_type_distribution,
                "chart_type_distribution": chart_type_distribution,
                "dashboard_type_distribution": dashboard_type_distribution,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting BI analytics: {e}")
            return {"error": str(e)}
    
    async def _collect_metrics(self):
        """Collect system metrics"""
        while self.running:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                await self._collect_frenly_metrics()
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"❌ Error collecting metrics: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.update_metric("system_cpu_usage", cpu_percent, {"type": "system"})
            
            # Memory usage
            memory = psutil.virtual_memory()
            await self.update_metric("system_memory_usage", memory.percent, {"type": "system"})
            
            # Disk usage
            disk = psutil.disk_usage('/')
            await self.update_metric("system_disk_usage", (disk.used / disk.total) * 100, {"type": "system"})
            
        except ImportError:
            logger.warning("psutil not available, skipping system metrics")
        except Exception as e:
            logger.error(f"❌ Error collecting system metrics: {e}")
    
    async def _collect_frenly_metrics(self):
        try:
            # This would collect actual Frenly AI metrics
            
            # Agent metrics
            await self.update_metric("agents_active", 5, {"type": "agent"})
            await self.update_metric("agents_total", 10, {"type": "agent"})
            
            # Task metrics
            await self.update_metric("tasks_completed", 150, {"type": "task"})
            await self.update_metric("tasks_failed", 5, {"type": "task"})
            
            # Performance metrics
            await self.update_metric("avg_response_time", 250, {"type": "performance", "unit": "ms"})
            await self.update_metric("requests_per_second", 100, {"type": "performance"})
            
        except Exception as e:
            logger.error(f"❌ Error collecting Frenly metrics: {e}")
    
    async def _refresh_charts(self):
        """Refresh chart data"""
        while self.running:
            try:
                for chart in self.charts.values():
                    # This would refresh chart data from data sources
                    # For now, we'll just log that we're refreshing
                    logger.debug(f"Refreshing chart: {chart.id}")
                
                await asyncio.sleep(self.chart_refresh_interval)
                
            except Exception as e:
                logger.error(f"❌ Error refreshing charts: {e}")
                await asyncio.sleep(60)
    
    async def _check_alerts(self):
        """Check alerts"""
        while self.running:
            try:
                for alert in self.alerts.values():
                    if not alert.enabled:
                        continue
                    
                    if alert.metric_id not in self.metrics:
                        continue
                    
                    metric = self.metrics[alert.metric_id]
                    
                    # Check alert condition
                    triggered = False
                    if alert.operator == ">":
                        triggered = metric.value > alert.threshold
                    elif alert.operator == "<":
                        triggered = metric.value < alert.threshold
                    elif alert.operator == ">=":
                        triggered = metric.value >= alert.threshold
                    elif alert.operator == "<=":
                        triggered = metric.value <= alert.threshold
                    elif alert.operator == "==":
                        triggered = metric.value == alert.threshold
                    elif alert.operator == "!=":
                        triggered = metric.value != alert.threshold
                    
                    if triggered:
                        alert.last_triggered = datetime.now().isoformat()
                        logger.warning(f"Alert triggered: {alert.name} - {metric.name} {alert.operator} {alert.threshold} (current: {metric.value})")
                
                await asyncio.sleep(self.alert_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error checking alerts: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics"""
        while self.running:
            try:
                cutoff_date = datetime.now() - timedelta(days=self.metric_retention_days)
                old_metrics = [
                    metric_id for metric_id, metric in self.metrics.items()
                    if datetime.fromisoformat(metric.timestamp) < cutoff_date
                ]
                
                for metric_id in old_metrics:
                    del self.metrics[metric_id]
                
                if old_metrics:
                    logger.info(f"Cleaned up {len(old_metrics)} old metrics")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old metrics: {e}")
                await asyncio.sleep(3600)
    
    async def _load_bi_data(self):
        """Load BI data from storage"""
        try:
            if self.redis_client:
                # Load metrics
                metrics_data = self.redis_client.get("frenly_bi_metrics")
                if metrics_data:
                    metrics_json = json.loads(metrics_data)
                    for metric_id, metric_data in metrics_json.items():
                        metric = Metric(
                            id=metric_id,
                            name=metric_data["name"],
                            description=metric_data["description"],
                            metric_type=MetricType(metric_data["metric_type"]),
                            value=metric_data["value"],
                            labels=metric_data.get("labels", {}),
                            timestamp=metric_data["timestamp"],
                            unit=metric_data.get("unit")
                        )
                        self.metrics[metric_id] = metric
                
                # Load charts
                charts_data = self.redis_client.get("frenly_bi_charts")
                if charts_data:
                    charts_json = json.loads(charts_data)
                    for chart_id, chart_data in charts_json.items():
                        chart = Chart(
                            id=chart_id,
                            title=chart_data["title"],
                            chart_type=ChartType(chart_data["chart_type"]),
                            data_source=chart_data["data_source"],
                            x_axis=chart_data["x_axis"],
                            y_axis=chart_data["y_axis"],
                            filters=chart_data.get("filters", {}),
                            config=chart_data.get("config", {}),
                            refresh_interval=chart_data.get("refresh_interval", 60)
                        )
                        self.charts[chart_id] = chart
                
                # Load dashboards
                dashboards_data = self.redis_client.get("frenly_bi_dashboards")
                if dashboards_data:
                    dashboards_json = json.loads(dashboards_data)
                    for dashboard_id, dashboard_data in dashboards_json.items():
                        # Get chart objects
                        chart_objects = []
                        for chart_id in dashboard_data.get("charts", []):
                            if chart_id in self.charts:
                                chart_objects.append(self.charts[chart_id])
                        
                        dashboard = Dashboard(
                            id=dashboard_id,
                            name=dashboard_data["name"],
                            description=dashboard_data["description"],
                            dashboard_type=DashboardType(dashboard_data["dashboard_type"]),
                            charts=chart_objects,
                            layout=dashboard_data.get("layout", {}),
                            filters=dashboard_data.get("filters", {}),
                            created_at=dashboard_data["created_at"],
                            updated_at=dashboard_data["updated_at"],
                            enabled=dashboard_data.get("enabled", True)
                        )
                        self.dashboards[dashboard_id] = dashboard
                
                # Load alerts
                alerts_data = self.redis_client.get("frenly_bi_alerts")
                if alerts_data:
                    alerts_json = json.loads(alerts_data)
                    for alert_id, alert_data in alerts_json.items():
                        alert = Alert(
                            id=alert_id,
                            name=alert_data["name"],
                            metric_id=alert_data["metric_id"],
                            condition=alert_data["condition"],
                            threshold=alert_data["threshold"],
                            operator=alert_data["operator"],
                            enabled=alert_data.get("enabled", True),
                            created_at=alert_data["created_at"],
                            last_triggered=alert_data.get("last_triggered")
                        )
                        self.alerts[alert_id] = alert
                
                logger.info(f"Loaded {len(self.metrics)} metrics, {len(self.charts)} charts, {len(self.dashboards)} dashboards, {len(self.alerts)} alerts")
            
        except Exception as e:
            logger.error(f"❌ Error loading BI data: {e}")
    
    async def _save_bi_data(self):
        """Save BI data to storage"""
        try:
            if self.redis_client:
                # Save metrics
                metrics_data = {
                    metric_id: {
                        "name": metric.name,
                        "description": metric.description,
                        "metric_type": metric.metric_type.value,
                        "value": metric.value,
                        "labels": metric.labels,
                        "timestamp": metric.timestamp,
                        "unit": metric.unit
                    }
                    for metric_id, metric in self.metrics.items()
                }
                self.redis_client.setex("frenly_bi_metrics", 86400, json.dumps(metrics_data))
                
                # Save charts
                charts_data = {
                    chart_id: {
                        "title": chart.title,
                        "chart_type": chart.chart_type.value,
                        "data_source": chart.data_source,
                        "x_axis": chart.x_axis,
                        "y_axis": chart.y_axis,
                        "filters": chart.filters,
                        "config": chart.config,
                        "refresh_interval": chart.refresh_interval
                    }
                    for chart_id, chart in self.charts.items()
                }
                self.redis_client.setex("frenly_bi_charts", 86400, json.dumps(charts_data))
                
                # Save dashboards
                dashboards_data = {
                    dashboard_id: {
                        "name": dashboard.name,
                        "description": dashboard.description,
                        "dashboard_type": dashboard.dashboard_type.value,
                        "charts": [chart.id for chart in dashboard.charts],
                        "layout": dashboard.layout,
                        "filters": dashboard.filters,
                        "created_at": dashboard.created_at,
                        "updated_at": dashboard.updated_at,
                        "enabled": dashboard.enabled
                    }
                    for dashboard_id, dashboard in self.dashboards.items()
                }
                self.redis_client.setex("frenly_bi_dashboards", 86400, json.dumps(dashboards_data))
                
                # Save alerts
                alerts_data = {
                    alert_id: {
                        "name": alert.name,
                        "metric_id": alert.metric_id,
                        "condition": alert.condition,
                        "threshold": alert.threshold,
                        "operator": alert.operator,
                        "enabled": alert.enabled,
                        "created_at": alert.created_at,
                        "last_triggered": alert.last_triggered
                    }
                    for alert_id, alert in self.alerts.items()
                }
                self.redis_client.setex("frenly_bi_alerts", 86400, json.dumps(alerts_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving BI data: {e}")

# Global BI dashboard instance
bi_dashboard = BIDashboard()
