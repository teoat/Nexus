/**
 * 🏠 Dashboard Layout Component
 * Main dashboard layout with sidebar, header, and content areas
 */

import React, { useState, useEffect } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { Avatar } from '../components/Avatar';

const dashboardLayoutVariants = cva(
  'min-h-screen bg-neutral-50',
  {
    variants: {
      sidebar: {
        collapsed: 'sidebar-collapsed',
        expanded: 'sidebar-expanded',
      },
      theme: {
        light: 'theme-light',
        dark: 'theme-dark',
      },
    },
    defaultVariants: {
      sidebar: 'expanded',
      theme: 'light',
    },
  }
);

export interface DashboardLayoutProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof dashboardLayoutVariants> {
  /**
   * Sidebar configuration
   */
  sidebar?: {
    items: SidebarItem[];
    collapsed?: boolean;
    onToggle?: (collapsed: boolean) => void;
    logo?: React.ReactNode;
    user?: {
      name: string;
      email: string;
      avatar?: string;
      role?: string;
    };
  };
  
  /**
   * Header configuration
   */
  header?: {
    title?: string;
    breadcrumbs?: BreadcrumbItem[];
    actions?: React.ReactNode;
    search?: {
      placeholder?: string;
      value?: string;
      onChange?: (value: string) => void;
    };
    notifications?: {
      count?: number;
      items?: NotificationItem[];
    };
    user?: {
      name: string;
      email: string;
      avatar?: string;
      menu?: React.ReactNode;
    };
  };
  
  /**
   * Main content
   */
  children: React.ReactNode;
  
  /**
   * Page title
   */
  pageTitle?: string;
  
  /**
   * Page description
   */
  pageDescription?: string;
  
  /**
   * Loading state
   */
  loading?: boolean;
  
  /**
   * Error state
   */
  error?: {
    title: string;
    message: string;
    action?: React.ReactNode;
  };
  
  /**
   * Footer content
   */
  footer?: React.ReactNode;
  
  /**
   * Custom sidebar content
   */
  sidebarContent?: React.ReactNode;
  
  /**
   * Custom header content
   */
  headerContent?: React.ReactNode;
}

export interface SidebarItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  href?: string;
  badge?: string | number;
  children?: SidebarItem[];
  disabled?: boolean;
  onClick?: () => void;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  time: string;
  unread?: boolean;
  type?: 'info' | 'success' | 'warning' | 'error';
}

const DashboardLayout = React.forwardRef<HTMLDivElement, DashboardLayoutProps>(
  (
    {
      className,
      sidebar: sidebarConfig,
      header: headerConfig,
      children,
      pageTitle,
      pageDescription,
      loading = false,
      error,
      footer,
      sidebarContent,
      headerContent,
      ...props
    },
    ref
  ) => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(sidebarConfig?.collapsed || false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [notificationsOpen, setNotificationsOpen] = useState(false);

    // Handle sidebar toggle
    const handleSidebarToggle = () => {
      const newCollapsed = !sidebarCollapsed;
      setSidebarCollapsed(newCollapsed);
      sidebarConfig?.onToggle?.(newCollapsed);
    };

    // Handle mobile menu toggle
    const handleMobileMenuToggle = () => {
      setMobileMenuOpen(!mobileMenuOpen);
    };

    // Handle notifications toggle
    const handleNotificationsToggle = () => {
      setNotificationsOpen(!notificationsOpen);
    };

    // Close mobile menu on resize
    useEffect(() => {
      const handleResize = () => {
        if (window.innerWidth >= 1024) {
          setMobileMenuOpen(false);
        }
      };

      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }, []);

    // Render sidebar
    const renderSidebar = () => {
      if (sidebarContent) {
        return sidebarContent;
      }

      return (
        <div className={cn(
          'flex flex-col h-full bg-white border-r border-neutral-200',
          sidebarCollapsed ? 'w-16' : 'w-64'
        )}>
          {/* Logo */}
          <div className="flex items-center justify-between p-4 border-b border-neutral-200">
            {!sidebarCollapsed && (
              <div className="flex items-center space-x-2">
                {sidebarConfig?.logo || (
                  <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-lg">N</span>
                  </div>
                )}
                <span className="text-xl font-bold text-neutral-900">Nexus</span>
              </div>
            )}
            
            <Button
              variant="ghost"
              size="sm"
              iconOnly
              onClick={handleSidebarToggle}
              className="lg:hidden"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {sidebarConfig?.items.map((item) => (
              <SidebarItemComponent
                key={item.key}
                item={item}
                collapsed={sidebarCollapsed}
              />
            ))}
          </nav>

          {/* User Section */}
          {sidebarConfig?.user && (
            <div className="p-4 border-t border-neutral-200">
              <div className={cn(
                'flex items-center space-x-3',
                sidebarCollapsed && 'justify-center'
              )}>
                <Avatar
                  src={sidebarConfig.user.avatar}
                  name={sidebarConfig.user.name}
                  size="sm"
                />
                {!sidebarCollapsed && (
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-neutral-900 truncate">
                      {sidebarConfig.user.name}
                    </p>
                    <p className="text-xs text-neutral-500 truncate">
                      {sidebarConfig.user.role || sidebarConfig.user.email}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      );
    };

    // Render header
    const renderHeader = () => {
      if (headerContent) {
        return headerContent;
      }

      return (
        <header className="bg-white border-b border-neutral-200 px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Left Section */}
            <div className="flex items-center space-x-4">
              {/* Mobile Menu Button */}
              <Button
                variant="ghost"
                size="sm"
                iconOnly
                onClick={handleMobileMenuToggle}
                className="lg:hidden"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </Button>

              {/* Breadcrumbs */}
              {headerConfig?.breadcrumbs && (
                <nav className="hidden md:flex items-center space-x-2 text-sm">
                  {headerConfig.breadcrumbs.map((item, index) => (
                    <React.Fragment key={index}>
                      {index > 0 && (
                        <svg className="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      )}
                      <a
                        href={item.href}
                        className="text-neutral-600 hover:text-neutral-900 flex items-center space-x-1"
                      >
                        {item.icon && <span>{item.icon}</span>}
                        <span>{item.label}</span>
                      </a>
                    </React.Fragment>
                  ))}
                </nav>
              )}

              {/* Page Title */}
              {headerConfig?.title && (
                <h1 className="text-xl font-semibold text-neutral-900">
                  {headerConfig.title}
                </h1>
              )}
            </div>

            {/* Right Section */}
            <div className="flex items-center space-x-4">
              {/* Search */}
              {headerConfig?.search && (
                <div className="hidden md:block">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder={headerConfig.search.placeholder || 'Search...'}
                      value={headerConfig.search.value || ''}
                      onChange={(e) => headerConfig.search?.onChange?.(e.target.value)}
                      className="w-64 pl-10 pr-4 py-2 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg className="w-4 h-4 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications */}
              {headerConfig?.notifications && (
                <div className="relative">
                  <Button
                    variant="ghost"
                    size="sm"
                    iconOnly
                    onClick={handleNotificationsToggle}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM9 12l2 2 4-4" />
                    </svg>
                    {headerConfig.notifications.count && headerConfig.notifications.count > 0 && (
                      <Badge
                        variant="error"
                        size="sm"
                        className="absolute -top-1 -right-1"
                      >
                        {headerConfig.notifications.count}
                      </Badge>
                    )}
                  </Button>

                  {/* Notifications Dropdown */}
                  {notificationsOpen && (
                    <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-neutral-200 z-50">
                      <div className="p-4 border-b border-neutral-200">
                        <h3 className="text-lg font-semibold text-neutral-900">Notifications</h3>
                      </div>
                      <div className="max-h-96 overflow-y-auto">
                        {headerConfig.notifications.items?.map((notification) => (
                          <div
                            key={notification.id}
                            className={cn(
                              'p-4 border-b border-neutral-100 hover:bg-neutral-50',
                              notification.unread && 'bg-primary-50'
                            )}
                          >
                            <div className="flex items-start space-x-3">
                              <div className={cn(
                                'w-2 h-2 rounded-full mt-2',
                                notification.type === 'success' && 'bg-success-500',
                                notification.type === 'warning' && 'bg-warning-500',
                                notification.type === 'error' && 'bg-error-500',
                                notification.type === 'info' && 'bg-primary-500'
                              )} />
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-neutral-900">
                                  {notification.title}
                                </p>
                                <p className="text-sm text-neutral-600 mt-1">
                                  {notification.message}
                                </p>
                                <p className="text-xs text-neutral-500 mt-1">
                                  {notification.time}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* User Menu */}
              {headerConfig?.user && (
                <div className="flex items-center space-x-3">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-medium text-neutral-900">
                      {headerConfig.user.name}
                    </p>
                    <p className="text-xs text-neutral-500">
                      {headerConfig.user.email}
                    </p>
                  </div>
                  <Avatar
                    src={headerConfig.user.avatar}
                    name={headerConfig.user.name}
                    size="sm"
                  />
                </div>
              )}

              {/* Actions */}
              {headerConfig?.actions && (
                <div className="flex items-center space-x-2">
                  {headerConfig.actions}
                </div>
              )}
            </div>
          </div>
        </header>
      );
    };

    return (
      <div ref={ref} className={cn(dashboardLayoutVariants({ sidebar: sidebarCollapsed ? 'collapsed' : 'expanded' }), className)} {...props}>
        <div className="flex h-screen">
          {/* Sidebar */}
          <div className={cn(
            'hidden lg:flex flex-col',
            sidebarCollapsed ? 'w-16' : 'w-64'
          )}>
            {renderSidebar()}
          </div>

          {/* Mobile Sidebar Overlay */}
          {mobileMenuOpen && (
            <div className="fixed inset-0 z-50 lg:hidden">
              <div className="fixed inset-0 bg-black bg-opacity-50" onClick={handleMobileMenuToggle} />
              <div className="relative flex flex-col w-64 h-full bg-white">
                {renderSidebar()}
              </div>
            </div>
          )}

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {renderHeader()}
            
            <main className="flex-1 overflow-auto">
              <div className="p-6">
                {/* Page Header */}
                {(pageTitle || pageDescription) && (
                  <div className="mb-6">
                    {pageTitle && (
                      <h1 className="text-2xl font-bold text-neutral-900 mb-2">
                        {pageTitle}
                      </h1>
                    )}
                    {pageDescription && (
                      <p className="text-neutral-600">
                        {pageDescription}
                      </p>
                    )}
                  </div>
                )}

                {/* Loading State */}
                {loading && (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  </div>
                )}

                {/* Error State */}
                {error && (
                  <Card variant="error" className="text-center py-12">
                    <h2 className="text-xl font-semibold text-error-900 mb-2">
                      {error.title}
                    </h2>
                    <p className="text-error-700 mb-4">
                      {error.message}
                    </p>
                    {error.action}
                  </Card>
                )}

                {/* Main Content */}
                {!loading && !error && children}
              </div>
            </main>

            {/* Footer */}
            {footer && (
              <footer className="bg-white border-t border-neutral-200 px-6 py-4">
                {footer}
              </footer>
            )}
          </div>
        </div>
      </div>
    );
  }
);

// Sidebar Item Component
const SidebarItemComponent = ({ item, collapsed }: { item: SidebarItem; collapsed: boolean }) => {
  const [expanded, setExpanded] = useState(false);

  const handleClick = () => {
    if (item.children) {
      setExpanded(!expanded);
    } else {
      item.onClick?.();
    }
  };

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={item.disabled}
        className={cn(
          'w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
          item.disabled
            ? 'text-neutral-400 cursor-not-allowed'
            : 'text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900'
        )}
      >
        {item.icon && <span className="flex-shrink-0">{item.icon}</span>}
        {!collapsed && (
          <>
            <span className="flex-1 text-left truncate">{item.label}</span>
            {item.badge && (
              <Badge variant="primary" size="sm">
                {item.badge}
              </Badge>
            )}
            {item.children && (
              <svg
                className={cn(
                  'w-4 h-4 transition-transform',
                  expanded && 'rotate-90'
                )}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            )}
          </>
        )}
      </button>

      {/* Submenu */}
      {item.children && expanded && !collapsed && (
        <div className="ml-4 mt-1 space-y-1">
          {item.children.map((child) => (
            <SidebarItemComponent key={child.key} item={child} collapsed={collapsed} />
          ))}
        </div>
      )}
    </div>
  );
};

DashboardLayout.displayName = 'DashboardLayout';

export { DashboardLayout, dashboardLayoutVariants };
export type { DashboardLayoutProps, SidebarItem, BreadcrumbItem, NotificationItem };
