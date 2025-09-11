import React, { useState } from 'react';
import Head from 'next/head';
import Layout from '@/components/layout/Layout';
import MetricsDashboard from '@/components/dashboard/MetricsDashboard';
import ServiceDashboards from '@/components/dashboard/ServiceDashboards';
import ServiceHealthMonitor from '@/components/monitoring/ServiceHealthMonitor';
import ServiceDiscovery from '@/components/services/ServiceDiscovery';
import CircuitBreakerMonitor from '@/components/monitoring/CircuitBreakerMonitor';
import LoadBalancerMonitor from '@/components/monitoring/LoadBalancerMonitor';
import APIGatewayMetrics from '@/components/monitoring/APIGatewayMetrics';
import DatabaseConnectionMonitor from '@/components/monitoring/DatabaseConnectionMonitor';
import MessageQueueMonitor from '@/components/monitoring/MessageQueueMonitor';
import CachePerformanceDashboard from '@/components/monitoring/CachePerformanceDashboard';
import ServiceDependenciesMap from '@/components/visualization/ServiceDependenciesMap';
import MultiDatabaseDashboard from '@/components/data/MultiDatabaseDashboard';
import QueryPerformanceMonitor from '@/components/performance/QueryPerformanceMonitor';
import DataConsistencyTools from '@/components/data/DataConsistencyTools';
import BackupManagementSystem from '@/components/backup/BackupManagementSystem';
import DataMigrationTools from '@/components/data/DataMigrationTools';
import IndexOptimizationInterface from '@/components/performance/IndexOptimizationInterface';
import StorageAnalyticsDashboard from '@/components/analytics/StorageAnalyticsDashboard';
import DataArchivingSystem from '@/components/data/DataArchivingSystem';
import SchemaManagementTools from '@/components/data/SchemaManagementTools';
import DataQualityMonitoring from '@/components/data/DataQualityMonitoring';
import ClusterManagementDashboard from '@/components/orchestration/ClusterManagementDashboard';
import NamespaceManagementInterface from '@/components/orchestration/NamespaceManagementInterface';
import PodMonitoringDashboard from '@/components/monitoring/PodMonitoringDashboard';
import ServiceMeshVisualization from '@/components/visualization/ServiceMeshVisualization';
import IngressManagementInterface from '@/components/orchestration/IngressManagementInterface';
import AutoScalingControls from '@/components/orchestration/AutoScalingControls';
import DeploymentStrategiesManagement from '@/components/orchestration/DeploymentStrategiesManagement';
import RollbackInterface from '@/components/orchestration/RollbackInterface';
import ResourceQuotasManagement from '@/components/orchestration/ResourceQuotasManagement';
import ResourceAllocationDashboard from '@/components/orchestration/ResourceAllocationDashboard';
import TaskSchedulingInterface from '@/components/automation/TaskSchedulingInterface';
import PerformanceMetricsDashboard from '@/components/monitoring/PerformanceMetricsDashboard';
import SystemHealthOverview from '@/components/monitoring/SystemHealthOverview';
import TaskTemplatesSystem from '@/components/automation/TaskTemplatesSystem';
import AIChatInterface from '@/components/ai/AIChatInterface';
import IntelligentRecommendationsSystem from '@/components/ai/IntelligentRecommendationsSystem';
import AnomalyDetectionDashboard from '@/components/ai/AnomalyDetectionDashboard';
import PredictiveAnalyticsInterface from '@/components/ai/PredictiveAnalyticsInterface';
import AutomatedTroubleshootingSystem from '@/components/ai/AutomatedTroubleshootingSystem';
import SmartAlertsSystem from '@/components/ai/SmartAlertsSystem';
import ResourceOptimizationAI from '@/components/ai/ResourceOptimizationAI';
import PerformanceTuningAI from '@/components/ai/PerformanceTuningAI';
import SecurityAnalysisAI from '@/components/ai/SecurityAnalysisAI';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useToast } from '@/components/ui/Toast';
import { 
  Plus, 
  Download, 
  Filter, 
  RefreshCw,
  TrendingUp,
  Users,
  Shield,
  Database,
  BarChart3,
  Monitor,
  Zap,
  Globe,
  MessageSquare,
  HardDrive,
  Activity,
  Server,
  Settings,
  Archive,
  GitBranch,
  Network,
  BarChart,
  Shield,
  Server,
  Folder,
  Activity,
  Globe,
  TrendingUp,
  RotateCcw,
  Gauge,
  Cpu,
  Calendar,
  BarChart3,
  Heart,
  FileText,
  Bot,
  Lightbulb,
  AlertTriangle,
  TrendingUp,
  Wrench,
  Bell,
  Shield
} from 'lucide-react';

interface DashboardTab {
  id: string;
  name: string;
  icon: React.ReactNode;
  component: React.ComponentType;
  description: string;
}

const DashboardPage: React.FC = () => {
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState('overview');

  const dashboardTabs: DashboardTab[] = [
    {
      id: 'overview',
      name: 'Overview',
      icon: <BarChart3 className="h-4 w-4" />,
      component: MetricsDashboard,
      description: 'High-level platform metrics and status'
    },
    {
      id: 'services',
      name: 'Service Dashboards',
      icon: <Server className="h-4 w-4" />,
      component: ServiceDashboards,
      description: 'Individual service monitoring and management'
    },
    {
      id: 'health',
      name: 'Service Health',
      icon: <Monitor className="h-4 w-4" />,
      component: ServiceHealthMonitor,
      description: 'Real-time service health monitoring'
    },
    {
      id: 'discovery',
      name: 'Service Discovery',
      icon: <Globe className="h-4 w-4" />,
      component: ServiceDiscovery,
      description: 'Service registry and endpoint management'
    },
    {
      id: 'circuit-breakers',
      name: 'Circuit Breakers',
      icon: <Zap className="h-4 w-4" />,
      component: CircuitBreakerMonitor,
      description: 'Circuit breaker states and failover'
    },
    {
      id: 'load-balancers',
      name: 'Load Balancers',
      icon: <Activity className="h-4 w-4" />,
      component: LoadBalancerMonitor,
      description: 'Load balancing and traffic distribution'
    },
    {
      id: 'api-gateway',
      name: 'API Gateway',
      icon: <Globe className="h-4 w-4" />,
      component: APIGatewayMetrics,
      description: 'API performance and rate limiting'
    },
    {
      id: 'database',
      name: 'Database',
      icon: <Database className="h-4 w-4" />,
      component: DatabaseConnectionMonitor,
      description: 'Database connection pools and performance'
    },
    {
      id: 'message-queue',
      name: 'Message Queue',
      icon: <MessageSquare className="h-4 w-4" />,
      component: MessageQueueMonitor,
      description: 'Message queue monitoring and processing'
    },
    {
      id: 'cache',
      name: 'Cache Performance',
      icon: <HardDrive className="h-4 w-4" />,
      component: CachePerformanceDashboard,
      description: 'Cache hit rates and memory usage'
    },
    {
      id: 'dependencies',
      name: 'Service Dependencies',
      icon: <Network className="h-4 w-4" />,
      component: ServiceDependenciesMap,
      description: 'Visual service interdependencies and data flow'
    },
    {
      id: 'multi-database',
      name: 'Multi-Database',
      icon: <Database className="h-4 w-4" />,
      component: MultiDatabaseDashboard,
      description: 'Unified interface for monitoring all data stores'
    },
    {
      id: 'query-performance',
      name: 'Query Performance',
      icon: <Zap className="h-4 w-4" />,
      component: QueryPerformanceMonitor,
      description: 'Real-time query performance monitoring'
    },
    {
      id: 'data-consistency',
      name: 'Data Consistency',
      icon: <Shield className="h-4 w-4" />,
      component: DataConsistencyTools,
      description: 'Tools for ensuring data consistency'
    },
    {
      id: 'backup-management',
      name: 'Backup Management',
      icon: <Archive className="h-4 w-4" />,
      component: BackupManagementSystem,
      description: 'Centralized backup scheduling and restoration'
    },
    {
      id: 'data-migration',
      name: 'Data Migration',
      icon: <Activity className="h-4 w-4" />,
      component: DataMigrationTools,
      description: 'UI for migrating data between storage systems'
    },
    {
      id: 'index-optimization',
      name: 'Index Optimization',
      icon: <Zap className="h-4 w-4" />,
      component: IndexOptimizationInterface,
      description: 'Database index management and optimization'
    },
    {
      id: 'storage-analytics',
      name: 'Storage Analytics',
      icon: <BarChart className="h-4 w-4" />,
      component: StorageAnalyticsDashboard,
      description: 'Track storage usage and growth patterns'
    },
    {
      id: 'data-archiving',
      name: 'Data Archiving',
      icon: <Archive className="h-4 w-4" />,
      component: DataArchivingSystem,
      description: 'Tools for archiving old data and retention policies'
    },
    {
      id: 'schema-management',
      name: 'Schema Management',
      icon: <GitBranch className="h-4 w-4" />,
      component: SchemaManagementTools,
      description: 'Database schema versioning and migration tools'
    },
    {
      id: 'data-quality',
      name: 'Data Quality',
      icon: <Shield className="h-4 w-4" />,
      component: DataQualityMonitoring,
      description: 'Data quality monitoring and improvement tools'
    },
    {
      id: 'cluster-management',
      name: 'Cluster Management',
      icon: <Server className="h-4 w-4" />,
      component: ClusterManagementDashboard,
      description: 'Kubernetes cluster health and resource monitoring'
    },
    {
      id: 'namespace-management',
      name: 'Namespace Management',
      icon: <Folder className="h-4 w-4" />,
      component: NamespaceManagementInterface,
      description: 'Multi-tenant namespace organization and resource allocation'
    },
    {
      id: 'pod-monitoring',
      name: 'Pod Monitoring',
      icon: <Activity className="h-4 w-4" />,
      component: PodMonitoringDashboard,
      description: 'Real-time pod status, restarts, and resource usage'
    },
    {
      id: 'service-mesh',
      name: 'Service Mesh',
      icon: <Network className="h-4 w-4" />,
      component: ServiceMeshVisualization,
      description: 'Istio traffic flow and policy visualization'
    },
    {
      id: 'ingress-management',
      name: 'Ingress Management',
      icon: <Globe className="h-4 w-4" />,
      component: IngressManagementInterface,
      description: 'Kong API Gateway configuration and traffic routing'
    },
    {
      id: 'auto-scaling',
      name: 'Auto-scaling',
      icon: <TrendingUp className="h-4 w-4" />,
      component: AutoScalingControls,
      description: 'HPA and VPA configuration and monitoring'
    },
    {
      id: 'deployment-strategies',
      name: 'Deployment Strategies',
      icon: <GitBranch className="h-4 w-4" />,
      component: DeploymentStrategiesManagement,
      description: 'Blue-green and canary deployment management'
    },
    {
      id: 'rollback-interface',
      name: 'Rollback Interface',
      icon: <RotateCcw className="h-4 w-4" />,
      component: RollbackInterface,
      description: 'Easy rollback to previous deployments'
    },
    {
      id: 'resource-quotas',
      name: 'Resource Quotas',
      icon: <Gauge className="h-4 w-4" />,
      component: ResourceQuotasManagement,
      description: 'Namespace resource limits and usage tracking'
    },
    {
      id: 'resource-allocation',
      name: 'Resource Allocation',
      icon: <Cpu className="h-4 w-4" />,
      component: ResourceAllocationDashboard,
      description: 'Worker resource allocation and optimization'
    },
    {
      id: 'task-scheduling',
      name: 'Task Scheduling',
      icon: <Calendar className="h-4 w-4" />,
      component: TaskSchedulingInterface,
      description: 'Automated task scheduling and execution'
    },
    {
      id: 'performance-metrics',
      name: 'Performance Metrics',
      icon: <BarChart3 className="h-4 w-4" />,
      component: PerformanceMetricsDashboard,
      description: 'Real-time system and application performance monitoring'
    },
    {
      id: 'system-health',
      name: 'System Health',
      icon: <Heart className="h-4 w-4" />,
      component: SystemHealthOverview,
      description: 'Real-time monitoring of all system components'
    },
    {
      id: 'task-templates',
      name: 'Task Templates',
      icon: <FileText className="h-4 w-4" />,
      component: TaskTemplatesSystem,
      description: 'Create, manage, and reuse task templates and workflows'
    },
    {
      id: 'ai-chat',
      name: 'AI Chat',
      icon: <Bot className="h-4 w-4" />,
      component: AIChatInterface,
      description: 'Natural language interface for system management'
    },
    {
      id: 'ai-recommendations',
      name: 'AI Recommendations',
      icon: <Lightbulb className="h-4 w-4" />,
      component: IntelligentRecommendationsSystem,
      description: 'AI-powered system optimization suggestions'
    },
    {
      id: 'anomaly-detection',
      name: 'Anomaly Detection',
      icon: <AlertTriangle className="h-4 w-4" />,
      component: AnomalyDetectionDashboard,
      description: 'AI-powered anomaly detection and alerting'
    },
    {
      id: 'predictive-analytics',
      name: 'Predictive Analytics',
      icon: <TrendingUp className="h-4 w-4" />,
      component: PredictiveAnalyticsInterface,
      description: 'Predictive system performance and capacity planning'
    },
    {
      id: 'automated-troubleshooting',
      name: 'Automated Troubleshooting',
      icon: <Wrench className="h-4 w-4" />,
      component: AutomatedTroubleshootingSystem,
      description: 'AI-assisted problem diagnosis and resolution'
    },
    {
      id: 'smart-alerts',
      name: 'Smart Alerts',
      icon: <Bell className="h-4 w-4" />,
      component: SmartAlertsSystem,
      description: 'Intelligent alert prioritization and grouping'
    },
    {
      id: 'resource-optimization-ai',
      name: 'Resource Optimization AI',
      icon: <Cpu className="h-4 w-4" />,
      component: ResourceOptimizationAI,
      description: 'AI-powered resource allocation optimization'
    },
    {
      id: 'performance-tuning-ai',
      name: 'Performance Tuning AI',
      icon: <Gauge className="h-4 w-4" />,
      component: PerformanceTuningAI,
      description: 'Automated performance tuning recommendations'
    },
    {
      id: 'security-analysis-ai',
      name: 'Security Analysis AI',
      icon: <Shield className="h-4 w-4" />,
      component: SecurityAnalysisAI,
      description: 'AI-powered security threat detection'
    }
  ];

  const handleRefresh = () => {
    addToast({
      type: 'info',
      title: 'Refreshing Data',
      description: 'Dashboard data is being updated...',
    });
  };

  const handleExport = () => {
    addToast({
      type: 'success',
      title: 'Export Started',
      description: 'Your dashboard data is being exported to CSV.',
    });
  };

  const mockUser = {
    name: 'John Doe',
    email: 'john.doe@nexus.com',
    avatar: undefined,
  };

  const ActiveComponent = dashboardTabs.find(tab => tab.id === activeTab)?.component || MetricsDashboard;

  return (
    <>
      <Head>
        <title>Dashboard - Nexus Platform</title>
        <meta name="description" content="Nexus Platform Dashboard - Real-time monitoring and management" />
      </Head>

      <Layout user={mockUser} notifications={3}>
        <div className="space-y-6">
          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Nexus Platform Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Comprehensive monitoring and management of all platform services
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={handleRefresh}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button variant="outline" onClick={handleExport}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Investigation
              </Button>
            </div>
          </div>

          {/* Dashboard Navigation */}
          <Card>
            <CardHeader>
              <CardTitle>Platform Monitoring</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2 mb-4">
                {dashboardTabs.map((tab) => (
                  <Button
                    key={tab.id}
                    variant={activeTab === tab.id ? 'default' : 'outline'}
                    onClick={() => setActiveTab(tab.id)}
                    className="flex items-center gap-2"
                  >
                    {tab.icon}
                    {tab.name}
                  </Button>
                ))}
              </div>
              
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  {dashboardTabs.find(tab => tab.id === activeTab)?.description}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Active Component */}
          <ActiveComponent />
        </div>
      </Layout>
    </>
  );
};

export default DashboardPage;