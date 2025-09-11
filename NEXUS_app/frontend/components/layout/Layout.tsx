import React, { ReactNode, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import Avatar from '../ai/Avatar';

interface LayoutProps {
  children: ReactNode;
  title?: string;
  showSidebar?: boolean;
  userRole?: 'investigator' | 'compliance' | 'executive' | 'admin';
}

export default function Layout({ 
  children, 
  title = "Nexus Platform", 
  showSidebar = true, 
  userRole = 'investigator' 
}: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const router = useRouter();

  const navigation = {
    investigator: [
      { name: 'Dashboard', href: '/dashboard', icon: '📊' },
      { name: 'Forensic Analysis', href: '/forensic-analysis', icon: '🔍' },
      { name: 'Evidence Management', href: '/evidence-management', icon: '📁' },
      { name: 'Reports', href: '/reports', icon: '📋' },
      { name: 'Case Management', href: '/cases', icon: '📂' }
    ],
    compliance: [
      { name: 'Dashboard', href: '/dashboard', icon: '📊' },
      { name: 'Risk Assessment', href: '/risk-assessment', icon: '⚠️' },
      { name: 'Compliance Monitoring', href: '/compliance', icon: '✅' },
      { name: 'Audit Trails', href: '/audit-trails', icon: '📜' },
      { name: 'Regulatory Reports', href: '/regulatory-reports', icon: '📄' }
    ],
    executive: [
      { name: 'Executive Dashboard', href: '/dashboard/executive', icon: '📊' },
      { name: 'Risk Overview', href: '/risk-overview', icon: '📈' },
      { name: 'Performance Metrics', href: '/performance', icon: '🎯' },
      { name: 'Strategic Reports', href: '/strategic-reports', icon: '📋' },
      { name: 'Team Management', href: '/team', icon: '👥' }
    ],
    admin: [
      { name: 'Admin Dashboard', href: '/dashboard/admin', icon: '⚙️' },
      { name: 'User Management', href: '/users', icon: '👤' },
      { name: 'System Configuration', href: '/config', icon: '🔧' },
      { name: 'Security Settings', href: '/security', icon: '🔒' },
      { name: 'System Logs', href: '/logs', icon: '📝' }
    ]
  };

  const handleAvatarInteraction = (action: string) => {
    switch (action) {
      case 'open-quickstart':
        router.push('/guide/quickstart');
        break;
      case 'optimize-dashboard':
        // Implement dashboard optimization
        console.log('Optimizing dashboard...');
        break;
      case 'workflow-help':
        // Open workflow help
        console.log('Opening workflow help...');
        break;
      case 'open-help':
        router.push('/guide/user-guide');
        break;
      case 'open-tutorials':
        router.push('/guide/tutorials');
        break;
      case 'open-feedback':
        // Open feedback modal
        console.log('Opening feedback...');
        break;
      case 'open-settings':
        router.push('/settings');
        break;
      default:
        console.log('Avatar action:', action);
    }
  };

  const currentContext = {
    currentPage: router.pathname,
    userRole: userRole,
    workflowStep: router.query.step as string,
    hasUnreadSuggestions: false // This would be determined by actual data
  };

  return (
    <div className="layout min-h-screen bg-gray-50">
      {/* Header */}
      <header className="header bg-white shadow-sm border-b border-gray-200">
        <div className="nav max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="nav-brand flex items-center">
              <Link href="/" className="flex items-center space-x-2">
                <h1 className="text-xl font-bold text-gray-900">🕵️ Nexus Platform</h1>
              </Link>
            </div>
            
            <div className="nav-links hidden md:flex items-center space-x-6">
              <Link 
                href="/dashboard" 
                className={`nav-link ${router.pathname === '/dashboard' ? 'active' : ''}`}
              >
                Dashboard
              </Link>
              <Link 
                href="/docs" 
                className={`nav-link ${router.pathname === '/docs' ? 'active' : ''}`}
              >
                Documentation
              </Link>
              <Link 
                href="/guide" 
                className={`nav-link ${router.pathname.startsWith('/guide') ? 'active' : ''}`}
              >
                Guides
              </Link>
              <Link 
                href="/support" 
                className={`nav-link ${router.pathname === '/support' ? 'active' : ''}`}
              >
                Support
              </Link>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="text-gray-500 hover:text-gray-700 focus:outline-none"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="main-layout flex">
        {/* Sidebar */}
        {showSidebar && (
          <aside className={`sidebar ${sidebarOpen ? 'open' : ''} bg-white shadow-lg border-r border-gray-200`}>
            <div className="sidebar-content p-4">
              <nav className="space-y-2">
                {navigation[userRole].map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`
                      sidebar-link flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors
                      ${router.pathname === item.href || router.pathname.startsWith(item.href + '/')
                        ? 'bg-blue-100 text-blue-700' 
                        : 'text-gray-700 hover:bg-gray-100'}
                    `}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <span className="mr-3">{item.icon}</span>
                    {item.name}
                  </Link>
                ))}
              </nav>

              {/* User Role Indicator */}
              <div className="mt-8 pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <span className="capitalize">{userRole}</span>
                </div>
              </div>
            </div>
          </aside>
        )}

        {/* Main Content */}
        <main className="main flex-1 p-6">
          {title && (
            <div className="mb-6">
              <h1 className="page-title text-2xl font-bold text-gray-900">{title}</h1>
            </div>
          )}
          {children}
        </main>
      </div>

      {/* Footer */}
      <footer className="footer bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <div className="flex items-center space-x-4">
              <span>&copy; 2024 Nexus Platform</span>
              <span>•</span>
              <Link href="/privacy" className="hover:text-gray-900">Privacy</Link>
              <span>•</span>
              <Link href="/terms" className="hover:text-gray-900">Terms</Link>
            </div>
            <div className="flex items-center space-x-2">
              <span>Powered by Frenly AI</span>
            </div>
          </div>
        </div>
      </footer>

      {/* AI Avatar */}
      <Avatar
        isVisible={true}
        context={currentContext}
        onInteraction={handleAvatarInteraction}
      />

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <style jsx>{`
        .layout {
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }

        .main-layout {
          flex: 1;
        }

        .sidebar {
          width: 280px;
          min-height: calc(100vh - 64px);
          transition: transform 0.3s ease-in-out;
          z-index: 50;
        }

        .sidebar.open {
          transform: translateX(0);
        }

        @media (max-width: 768px) {
          .sidebar {
            position: fixed;
            top: 64px;
            left: 0;
            transform: translateX(-100%);
            height: calc(100vh - 64px);
          }
        }

        .nav-link {
          color: #6b7280;
          text-decoration: none;
          font-weight: 500;
          transition: color 0.2s;
        }

        .nav-link:hover {
          color: #374151;
        }

        .nav-link.active {
          color: #2563eb;
        }

        .sidebar-link {
          text-decoration: none;
          display: flex;
          align-items: center;
          padding: 0.5rem 0.75rem;
          border-radius: 0.5rem;
          font-size: 0.875rem;
          font-weight: 500;
          transition: all 0.2s;
        }
      `}</style>
    </div>
  );
}
