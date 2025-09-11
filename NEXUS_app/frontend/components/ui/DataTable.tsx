/**
 * 📊 DataTable Component
 * Advanced data table with sorting, filtering, pagination, and selection
 */

import React, { useState, useMemo, useCallback } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';
import { Button } from './Button';
import { Input } from './Input';
import { Select } from './Select';
import { Checkbox } from './Checkbox';
import { Badge } from './Badge';

const dataTableVariants = cva(
  'w-full border-collapse',
  {
    variants: {
      variant: {
        default: 'bg-white',
        striped: 'bg-white [&_tbody_tr:nth-child(odd)]:bg-neutral-50',
        bordered: 'border border-neutral-200',
        hover: 'bg-white [&_tbody_tr:hover]:bg-neutral-50',
      },
      size: {
        sm: 'text-sm',
        md: 'text-sm',
        lg: 'text-base',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

export interface Column<T> {
  key: keyof T | string;
  title: string;
  dataIndex?: keyof T;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  sortable?: boolean;
  filterable?: boolean;
  width?: string | number;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
  ellipsis?: boolean;
  sorter?: (a: T, b: T) => number;
  filters?: Array<{ text: string; value: any }>;
  onFilter?: (value: any, record: T) => boolean;
}

export interface DataTableProps<T = any>
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof dataTableVariants> {
  /**
   * Data source
   */
  data: T[];
  
  /**
   * Column configuration
   */
  columns: Column<T>[];
  
  /**
   * Loading state
   */
  loading?: boolean;
  
  /**
   * Row selection configuration
   */
  rowSelection?: {
    type?: 'checkbox' | 'radio';
    selectedRowKeys?: React.Key[];
    onChange?: (selectedRowKeys: React.Key[], selectedRows: T[]) => void;
    getCheckboxProps?: (record: T) => { disabled?: boolean; name?: string };
  };
  
  /**
   * Pagination configuration
   */
  pagination?: {
    current?: number;
    pageSize?: number;
    total?: number;
    showSizeChanger?: boolean;
    showQuickJumper?: boolean;
    showTotal?: (total: number, range: [number, number]) => string;
    onChange?: (page: number, pageSize: number) => void;
  };
  
  /**
   * Sorting configuration
   */
  sortConfig?: {
    key?: string;
    direction?: 'asc' | 'desc';
    onChange?: (key: string, direction: 'asc' | 'desc') => void;
  };
  
  /**
   * Filtering configuration
   */
  filters?: Record<string, any>;
  onFilterChange?: (filters: Record<string, any>) => void;
  
  /**
   * Search configuration
   */
  search?: {
    placeholder?: string;
    value?: string;
    onChange?: (value: string) => void;
  };
  
  /**
   * Empty state
   */
  emptyText?: string;
  emptyDescription?: string;
  
  /**
   * Row key function
   */
  rowKey?: (record: T) => React.Key;
  
  /**
   * Row className function
   */
  rowClassName?: (record: T, index: number) => string;
  
  /**
   * Expandable rows
   */
  expandable?: {
    expandedRowKeys?: React.Key[];
    onExpandedRowsChange?: (expandedKeys: React.Key[]) => void;
    expandedRowRender?: (record: T, index: number) => React.ReactNode;
    expandRowByClick?: boolean;
  };
  
  /**
   * Sticky header
   */
  sticky?: boolean;
  
  /**
   * Virtual scrolling
   */
  virtual?: boolean;
  height?: number;
}

const DataTable = <T extends Record<string, any>>({
  className,
  variant,
  size,
  data,
  columns,
  loading = false,
  rowSelection,
  pagination,
  sortConfig,
  filters = {},
  onFilterChange,
  search,
  emptyText = 'No data',
  emptyDescription,
  rowKey = (record, index) => (record as any).id || index,
  rowClassName,
  expandable,
  sticky = false,
  virtual = false,
  height,
  ...props
}: DataTableProps<T>) => {
  const [internalSortConfig, setInternalSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);
  
  const [internalFilters, setInternalFilters] = useState<Record<string, any>>(filters);
  const [internalSearch, setInternalSearch] = useState(search?.value || '');
  const [expandedRows, setExpandedRows] = useState<React.Key[]>(expandable?.expandedRowKeys || []);

  // Process data with sorting, filtering, and searching
  const processedData = useMemo(() => {
    let result = [...data];

    // Apply search
    if (internalSearch) {
      result = result.filter((record) => {
        return columns.some((column) => {
          const value = column.dataIndex ? record[column.dataIndex] : (record as any)[column.key];
          return String(value).toLowerCase().includes(internalSearch.toLowerCase());
        });
      });
    }

    // Apply filters
    Object.entries(internalFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        const column = columns.find(col => col.key === key);
        if (column?.onFilter) {
          result = result.filter(record => column.onFilter!(value, record));
        }
      }
    });

    // Apply sorting
    const currentSortConfig = sortConfig || internalSortConfig;
    if (currentSortConfig) {
      result.sort((a, b) => {
        const column = columns.find(col => col.key === currentSortConfig.key);
        if (column?.sorter) {
          return column.sorter(a, b);
        }
        
        const aValue = column?.dataIndex ? a[column.dataIndex] : (a as any)[column?.key || ''];
        const bValue = column?.dataIndex ? b[column.dataIndex] : (b as any)[column?.key || ''];
        
        if (aValue < bValue) return currentSortConfig.direction === 'asc' ? -1 : 1;
        if (aValue > bValue) return currentSortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [data, columns, internalSearch, internalFilters, sortConfig, internalSortConfig]);

  // Handle sorting
  const handleSort = useCallback((key: string) => {
    const column = columns.find(col => col.key === key);
    if (!column?.sortable) return;

    const newDirection = 
      internalSortConfig?.key === key && internalSortConfig.direction === 'asc' 
        ? 'desc' 
        : 'asc';

    setInternalSortConfig({ key, direction: newDirection });
    sortConfig?.onChange?.(key, newDirection);
  }, [columns, internalSortConfig, sortConfig]);

  // Handle filter change
  const handleFilterChange = useCallback((key: string, value: any) => {
    const newFilters = { ...internalFilters, [key]: value };
    setInternalFilters(newFilters);
    onFilterChange?.(newFilters);
  }, [internalFilters, onFilterChange]);

  // Handle search change
  const handleSearchChange = useCallback((value: string) => {
    setInternalSearch(value);
    search?.onChange?.(value);
  }, [search]);

  // Handle row selection
  const handleRowSelection = useCallback((record: T, checked: boolean) => {
    if (!rowSelection) return;
    
    const key = rowKey(record);
    const currentKeys = rowSelection.selectedRowKeys || [];
    const newKeys = checked 
      ? [...currentKeys, key]
      : currentKeys.filter(k => k !== key);
    
    const newRows = data.filter(record => newKeys.includes(rowKey(record)));
    rowSelection.onChange?.(newKeys, newRows);
  }, [rowSelection, data, rowKey]);

  // Handle select all
  const handleSelectAll = useCallback((checked: boolean) => {
    if (!rowSelection) return;
    
    const keys = checked ? processedData.map(record => rowKey(record)) : [];
    const rows = checked ? processedData : [];
    rowSelection.onChange?.(keys, rows);
  }, [rowSelection, processedData, rowKey]);

  // Handle row expansion
  const handleRowExpand = useCallback((key: React.Key) => {
    const newExpandedRows = expandedRows.includes(key)
      ? expandedRows.filter(k => k !== key)
      : [...expandedRows, key];
    
    setExpandedRows(newExpandedRows);
    expandable?.onExpandedRowsChange?.(newExpandedRows);
  }, [expandedRows, expandable]);

  // Render loading state
  if (loading) {
    return (
      <div className="w-full">
        <div className="animate-pulse">
          <div className="h-10 bg-neutral-200 rounded mb-4"></div>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-12 bg-neutral-100 rounded mb-2"></div>
          ))}
        </div>
      </div>
    );
  }

  // Render empty state
  if (processedData.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-neutral-500 text-lg font-medium mb-2">
          {emptyText}
        </div>
        {emptyDescription && (
          <div className="text-neutral-400 text-sm">
            {emptyDescription}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={cn('w-full', className)} {...props}>
      {/* Search and Filters */}
      {(search || columns.some(col => col.filterable)) && (
        <div className="mb-4 flex flex-wrap gap-4">
          {search && (
            <div className="flex-1 min-w-64">
              <Input
                placeholder={search.placeholder || 'Search...'}
                value={internalSearch}
                onChange={(e) => handleSearchChange(e.target.value)}
                leftIcon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                }
              />
            </div>
          )}
          
          {columns
            .filter(col => col.filterable && col.filters)
            .map(column => (
              <div key={String(column.key)} className="min-w-32">
                <Select
                  placeholder={`Filter ${column.title}`}
                  value={internalFilters[String(column.key)]}
                  onChange={(value) => handleFilterChange(String(column.key), value)}
                  options={column.filters?.map(filter => ({
                    label: filter.text,
                    value: filter.value,
                  }))}
                />
              </div>
            ))}
        </div>
      )}

      {/* Table */}
      <div className={cn('overflow-x-auto', sticky && 'max-h-96 overflow-y-auto')}>
        <table className={cn(dataTableVariants({ variant, size }))}>
          <thead className={cn(sticky && 'sticky top-0 z-10 bg-white')}>
            <tr>
              {/* Selection Column */}
              {rowSelection && (
                <th className="w-12 px-4 py-3 text-left">
                  {rowSelection.type === 'checkbox' && (
                    <Checkbox
                      checked={processedData.length > 0 && processedData.every(record => 
                        (rowSelection.selectedRowKeys || []).includes(rowKey(record))
                      )}
                      indeterminate={
                        processedData.some(record => 
                          (rowSelection.selectedRowKeys || []).includes(rowKey(record))
                        ) && !processedData.every(record => 
                          (rowSelection.selectedRowKeys || []).includes(rowKey(record))
                        )
                      }
                      onChange={(checked) => handleSelectAll(checked)}
                    />
                  )}
                </th>
              )}
              
              {/* Expand Column */}
              {expandable && (
                <th className="w-12 px-4 py-3 text-left"></th>
              )}
              
              {/* Data Columns */}
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className={cn(
                    'px-4 py-3 text-left font-medium text-neutral-700',
                    column.align === 'center' && 'text-center',
                    column.align === 'right' && 'text-right',
                    column.sortable && 'cursor-pointer hover:bg-neutral-50',
                    column.fixed === 'left' && 'sticky left-0 bg-white z-10',
                    column.fixed === 'right' && 'sticky right-0 bg-white z-10'
                  )}
                  style={{ width: column.width }}
                  onClick={() => column.sortable && handleSort(String(column.key))}
                >
                  <div className="flex items-center space-x-1">
                    <span>{column.title}</span>
                    {column.sortable && (
                      <div className="flex flex-col">
                        <svg
                          className={cn(
                            'w-3 h-3',
                            internalSortConfig?.key === column.key && internalSortConfig.direction === 'asc'
                              ? 'text-primary-600'
                              : 'text-neutral-400'
                          )}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M5 12l5-5 5 5H5z" />
                        </svg>
                        <svg
                          className={cn(
                            'w-3 h-3 -mt-1',
                            internalSortConfig?.key === column.key && internalSortConfig.direction === 'desc'
                              ? 'text-primary-600'
                              : 'text-neutral-400'
                          )}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M15 8l-5 5-5-5h10z" />
                        </svg>
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          
          <tbody>
            {processedData.map((record, index) => {
              const key = rowKey(record);
              const isExpanded = expandedRows.includes(key);
              const isSelected = (rowSelection?.selectedRowKeys || []).includes(key);
              
              return (
                <React.Fragment key={key}>
                  <tr
                    className={cn(
                      'border-b border-neutral-200 hover:bg-neutral-50',
                      isSelected && 'bg-primary-50',
                      rowClassName?.(record, index)
                    )}
                  >
                    {/* Selection Cell */}
                    {rowSelection && (
                      <td className="px-4 py-3">
                        {rowSelection.type === 'checkbox' ? (
                          <Checkbox
                            checked={isSelected}
                            onChange={(checked) => handleRowSelection(record, checked)}
                            {...rowSelection.getCheckboxProps?.(record)}
                          />
                        ) : (
                          <input
                            type="radio"
                            checked={isSelected}
                            onChange={() => handleRowSelection(record, true)}
                            className="text-primary-600"
                          />
                        )}
                      </td>
                    )}
                    
                    {/* Expand Cell */}
                    {expandable && (
                      <td className="px-4 py-3">
                        <Button
                          variant="ghost"
                          size="sm"
                          iconOnly
                          onClick={() => handleRowExpand(key)}
                        >
                          <svg
                            className={cn(
                              'w-4 h-4 transition-transform',
                              isExpanded && 'rotate-90'
                            )}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </Button>
                      </td>
                    )}
                    
                    {/* Data Cells */}
                    {columns.map((column) => {
                      const value = column.dataIndex ? record[column.dataIndex] : (record as any)[column.key];
                      const cellContent = column.render ? column.render(value, record, index) : value;
                      
                      return (
                        <td
                          key={String(column.key)}
                          className={cn(
                            'px-4 py-3',
                            column.align === 'center' && 'text-center',
                            column.align === 'right' && 'text-right',
                            column.ellipsis && 'truncate',
                            column.fixed === 'left' && 'sticky left-0 bg-white z-10',
                            column.fixed === 'right' && 'sticky right-0 bg-white z-10'
                          )}
                          style={{ width: column.width }}
                        >
                          {cellContent}
                        </td>
                      );
                    })}
                  </tr>
                  
                  {/* Expanded Row */}
                  {expandable && isExpanded && expandable.expandedRowRender && (
                    <tr>
                      <td
                        colSpan={columns.length + (rowSelection ? 1 : 0) + (expandable ? 1 : 0)}
                        className="px-4 py-3 bg-neutral-50"
                      >
                        {expandable.expandedRowRender(record, index)}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && (
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-neutral-600">
            {pagination.showTotal ? (
              pagination.showTotal(
                pagination.total || processedData.length,
                [1, pagination.pageSize || 10]
              )
            ) : (
              `Showing ${((pagination.current || 1) - 1) * (pagination.pageSize || 10) + 1} to ${Math.min(
                (pagination.current || 1) * (pagination.pageSize || 10),
                pagination.total || processedData.length
              )} of ${pagination.total || processedData.length} entries`
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.current || pagination.current <= 1}
              onClick={() => pagination.onChange?.(pagination.current! - 1, pagination.pageSize!)}
            >
              Previous
            </Button>
            
            <span className="text-sm text-neutral-600">
              Page {pagination.current || 1} of {Math.ceil((pagination.total || processedData.length) / (pagination.pageSize || 10))}
            </span>
            
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.current || pagination.current >= Math.ceil((pagination.total || processedData.length) / (pagination.pageSize || 10))}
              onClick={() => pagination.onChange?.(pagination.current! + 1, pagination.pageSize!)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};

export { DataTable, dataTableVariants };
export type { DataTableProps, Column };
