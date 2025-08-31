"""
Performance Dashboard for Nexus Platform

Implements real-time and historical data visualization for queue metrics.
"""

import asyncio
import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Types of charts."""
    LINE = "line"
    BAR = "bar"
    TABLE = "table"
    GAUGE = "gauge"

@dataclass
class DashboardWidget:
    """Dashboard widget configuration."""
    id: str
    name: str
    chart_type: ChartType
    data_source: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    name: str
    widgets: List[DashboardWidget]
    theme: str = "dark"

class PerformanceDashboard:
    """Real-time performance dashboard for queue metrics."""

    def __init__(self, metrics_collector=None):
        """Initializes the PerformanceDashboard."""
        self.metrics_collector = metrics_collector
        self.dashboards: Dict[str, DashboardConfig] = {}
        self._create_default_dashboard()
        logger.info("Performance Dashboard initialized")

    def _create_default_dashboard(self):
        """Creates a default dashboard with common widgets."""
        default_widgets = [
            DashboardWidget(id="queue_overview", name="Queue Overview", chart_type=ChartType.TABLE, data_source="queue_stats", position=(0, 0), size=(12, 4)),
            DashboardWidget(id="throughput_trend", name="Throughput Trend", chart_type=ChartType.LINE, data_source="throughput_history", position=(0, 4), size=(6, 4)),
            DashboardWidget(id="latency_dist", name="Latency Distribution", chart_type=ChartType.BAR, data_source="latency_history", position=(6, 4), size=(6, 4)),
        ]
        default_dashboard = DashboardConfig(name="Default Dashboard", widgets=default_widgets)
        self.dashboards["default"] = default_dashboard
        logger.info("Default dashboard created")

    async def get_dashboard_data(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """Gets the current data for a dashboard."""
        if dashboard_id not in self.dashboards:
            return None
        
        dashboard = self.dashboards[dashboard_id]
        dashboard_data = {
            "name": dashboard.name,
            "widgets": []
        }

        for widget in dashboard.widgets:
            widget_data = {"id": widget.id, "name": widget.name, "type": widget.chart_type.value}
            # In a real implementation, this would fetch data from the metrics_collector
            widget_data["data"] = {"mock_data": f"Data for {widget.name}"}
            dashboard_data["widgets"].append(widget_data)
        
        return dashboard_data

def test_performance_dashboard():
    """Tests the Performance Dashboard."""
    logging.basicConfig(level=logging.INFO)
    print("🧪 Testing Performance Dashboard")
    dashboard = PerformanceDashboard()
    
    async def main():
        data = await dashboard.get_dashboard_data("default")
        if data:
            print(f"Dashboard: {data['name']}")
            print(f"  Widgets: {len(data['widgets'])}")
            for w in data['widgets']:
                print(f"    - {w['name']} ({w['type']})")

    asyncio.run(main())

if __name__ == "__main__":
    test_performance_dashboard()
