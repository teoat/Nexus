/**
 * 📊 Analytics Dashboard Component
 * Comprehensive analytics dashboard with charts, metrics, and data visualization
 */

import React, { useState, useMemo } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';
import { Card } from './Card';
import { Button } from './Button';
import { Select } from './Select';
import { Badge } from './Badge';

const analyticsDashboardVariants = cva(
  'w-full space-y-6',
  {
    variants: {
      layout: {
        grid: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6',
        list: 'flex flex-col space-y-6',
        compact: 'grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4',
      },
      theme: {
        light: 'bg-white',
        dark: 'bg-neutral-900',
      },
    },
    defaultVariants: {
      layout: 'grid',
      theme: 'light',
    },
  }
);

export interface MetricData {
  id: string;
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease' | 'neutral';
  };
  trend?: {
    data: number[];
    period: string;
  };
  icon?: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
  format?: 'number' | 'currency' | 'percentage' | 'duration';
}

export interface ChartData {
  id: string;
  title: string;
  type: 'line' | 'bar' | 'pie' | 'area' | 'donut' | 'scatter';
  data: any[];
  options?: any;
  height?: number;
  color?: string;
}

export interface AnalyticsDashboardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof analyticsDashboardVariants> {
  /**
   * Dashboard title
   */
  title?: string;
  
  /**
   * Dashboard description
   */
  description?: string;
  
  /**
   * Time period options
   */
  timePeriods?: Array<{ label: string; value: string }>;
  
  /**
   * Selected time period
   */
  selectedPeriod?: string;
  
  /**
   * Time period change handler
   */
  onPeriodChange?: (period: string) => void;
  
  /**
   * Metrics data
   */
  metrics?: MetricData[];
  
  /**
   * Charts data
   */
  charts?: ChartData[];
  
  /**
   * Loading state
   */
  loading?: boolean;
  
  /**
   * Refresh handler
   */
  onRefresh?: () => void;
  
  /**
   * Export handler
   */
  onExport?: (format: 'pdf' | 'excel' | 'csv') => void;
  
  /**
   * Custom actions
   */
  actions?: React.ReactNode;
  
  /**
   * Real-time updates
   */
  realTime?: boolean;
  
  /**
   * Last updated timestamp
   */
  lastUpdated?: Date;
}

const AnalyticsDashboard = React.forwardRef<HTMLDivElement, AnalyticsDashboardProps>(
  (
    {
      className,
      layout,
      theme,
      title = 'Analytics Dashboard',
      description,
      timePeriods = [
        { label: 'Last 7 days', value: '7d' },
        { label: 'Last 30 days', value: '30d' },
        { label: 'Last 90 days', value: '90d' },
        { label: 'Last year', value: '1y' },
      ],
      selectedPeriod = '7d',
      onPeriodChange,
      metrics = [],
      charts = [],
      loading = false,
      onRefresh,
      onExport,
      actions,
      realTime = false,
      lastUpdated,
      ...props
    },
    ref
  ) => {
    const [refreshing, setRefreshing] = useState(false);

    // Handle refresh
    const handleRefresh = async () => {
      if (onRefresh) {
        setRefreshing(true);
        try {
          await onRefresh();
        } finally {
          setRefreshing(false);
        }
      }
    };

    // Handle export
    const handleExport = (format: 'pdf' | 'excel' | 'csv') => {
      onExport?.(format);
    };

    // Format metric value
    const formatMetricValue = (value: string | number, format?: string) => {
      if (typeof value === 'string') return value;
      
      switch (format) {
        case 'currency':
          return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
          }).format(value);
        case 'percentage':
          return `${value}%`;
        case 'duration':
          return `${value}s`;
        default:
          return new Intl.NumberFormat('en-US').format(value);
      }
    };

    // Get change color
    const getChangeColor = (change: MetricData['change']) => {
      if (!change) return 'text-neutral-500';
      
      switch (change.type) {
        case 'increase':
          return 'text-success-600';
        case 'decrease':
          return 'text-error-600';
        default:
          return 'text-neutral-500';
      }
    };

    // Get change icon
    const getChangeIcon = (change: MetricData['change']) => {
      if (!change) return null;
      
      switch (change.type) {
        case 'increase':
          return (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 17l9.2-9.2M17 17V7H7" />
            </svg>
          );
        case 'decrease':
          return (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 7l-9.2 9.2M7 7v10h10" />
            </svg>
          );
        default:
          return null;
      }
    };

    // Render metric card
    const renderMetricCard = (metric: MetricData) => (
      <Card
        key={metric.id}
        className="p-6 hover:shadow-md transition-shadow"
        variant={metric.color === 'error' ? 'error' : metric.color === 'warning' ? 'warning' : 'default'}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {metric.icon && (
                <div className={cn(
                  'p-2 rounded-lg',
                  metric.color === 'primary' && 'bg-primary-100 text-primary-600',
                  metric.color === 'success' && 'bg-success-100 text-success-600',
                  metric.color === 'warning' && 'bg-warning-100 text-warning-600',
                  metric.color === 'error' && 'bg-error-100 text-error-600',
                  metric.color === 'info' && 'bg-info-100 text-info-600',
                  !metric.color && 'bg-neutral-100 text-neutral-600'
                )}>
                  {metric.icon}
                </div>
              )}
              <h3 className="text-sm font-medium text-neutral-600 truncate">
                {metric.title}
              </h3>
            </div>
            
            <div className="text-2xl font-bold text-neutral-900 mb-2">
              {formatMetricValue(metric.value, metric.format)}
            </div>
            
            {metric.change && (
              <div className={cn('flex items-center space-x-1 text-sm', getChangeColor(metric.change))}>
                {getChangeIcon(metric.change)}
                <span>
                  {metric.change.type === 'increase' ? '+' : metric.change.type === 'decrease' ? '-' : ''}
                  {Math.abs(metric.change.value)}%
                </span>
                <span className="text-neutral-500">vs last period</span>
              </div>
            )}
          </div>
        </div>
      </Card>
    );

    // Render chart card
    const renderChartCard = (chart: ChartData) => (
      <Card
        key={chart.id}
        className="p-6"
        style={{ height: chart.height || 300 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-neutral-900">
            {chart.title}
          </h3>
          <div className="flex items-center space-x-2">
            {chart.color && (
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: chart.color }}
              />
            )}
            <Button variant="ghost" size="sm" iconOnly>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </Button>
          </div>
        </div>
        
        <div className="h-full">
          {/* Placeholder for chart - in real implementation, use a chart library like Recharts */}
          <div className="w-full h-full bg-neutral-50 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <div className="text-neutral-400 text-sm mb-2">
                {chart.type.toUpperCase()} Chart
              </div>
              <div className="text-xs text-neutral-500">
                {chart.data.length} data points
              </div>
            </div>
          </div>
        </div>
      </Card>
    );

    return (
      <div ref={ref} className={cn(analyticsDashboardVariants({ layout, theme }), className)} {...props}>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900">
              {title}
            </h1>
            {description && (
              <p className="text-neutral-600 mt-1">
                {description}
              </p>
            )}
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Time Period Selector */}
            <Select
              value={selectedPeriod}
              onChange={(value) => onPeriodChange?.(value)}
              options={timePeriods}
              className="min-w-32"
            />
            
            {/* Refresh Button */}
            {onRefresh && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                loading={refreshing}
                iconOnly
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </Button>
            )}
            
            {/* Export Button */}
            {onExport && (
              <div className="relative">
                <Button
                  variant="outline"
                  size="sm"
                  rightIcon={
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  }
                >
                  Export
                </Button>
                {/* Export dropdown would go here */}
              </div>
            )}
            
            {/* Real-time Indicator */}
            {realTime && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                <span className="text-sm text-neutral-600">Live</span>
              </div>
            )}
            
            {/* Last Updated */}
            {lastUpdated && (
              <div className="text-sm text-neutral-500">
                Updated {lastUpdated.toLocaleTimeString()}
              </div>
            )}
            
            {/* Custom Actions */}
            {actions}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        )}

        {/* Content */}
        {!loading && (
          <>
            {/* Metrics Grid */}
            {metrics.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {metrics.map(renderMetricCard)}
              </div>
            )}

            {/* Charts Grid */}
            {charts.length > 0 && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {charts.map(renderChartCard)}
              </div>
            )}

            {/* Empty State */}
            {metrics.length === 0 && charts.length === 0 && (
              <Card className="text-center py-12">
                <div className="text-neutral-400 text-lg font-medium mb-2">
                  No analytics data available
                </div>
                <p className="text-neutral-500 text-sm">
                  Data will appear here once it's available
                </p>
              </Card>
            )}
          </>
        )}
      </div>
    );
  }
);

AnalyticsDashboard.displayName = 'AnalyticsDashboard';

export { AnalyticsDashboard, analyticsDashboardVariants };
export type { AnalyticsDashboardProps, MetricData, ChartData };
