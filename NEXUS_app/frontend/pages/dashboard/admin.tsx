// NEXUS_app/frontend/pages/dashboard/admin.tsx
import Layout from '../../components/Layout';
import { useState, useEffect } from 'react';

export default function AdminDashboard() {
  const [systemHealth, setSystemHealth] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0
  });
  const [users, setUsers] = useState([]);
  const [services, setServices] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    // Simulate real-time system monitoring
    const interval = setInterval(() => {
      setSystemHealth({
        cpu: Math.floor(Math.random() * 100),
        memory: Math.floor(Math.random() * 100),
        disk: Math.floor(Math.random() * 100),
        network: Math.floor(Math.random() * 100)
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Layout title="System Administration" userRole="admin">
      <div className="admin-dashboard">
        {/* System Health Overview */}
        <div className="system-health">
          <h2>System Health Overview</h2>
          <div className="health-grid">
            <div className="health-card">
              <div className="health-header">
                <h3>CPU Usage</h3>
                <span className={`health-status ${systemHealth.cpu > 80 ? 'critical' : systemHealth.cpu > 60 ? 'warning' : 'healthy'}`}>
                  {systemHealth.cpu > 80 ? 'Critical' : systemHealth.cpu > 60 ? 'Warning' : 'Healthy'}
                </span>
              </div>
              <div className="health-value">{systemHealth.cpu}%</div>
              <div className="health-bar">
                <div className="health-fill" style={{width: `${systemHealth.cpu}%`}}></div>
              </div>
            </div>

            <div className="health-card">
              <div className="health-header">
                <h3>Memory Usage</h3>
                <span className={`health-status ${systemHealth.memory > 80 ? 'critical' : systemHealth.memory > 60 ? 'warning' : 'healthy'}`}>
                  {systemHealth.memory > 80 ? 'Critical' : systemHealth.memory > 60 ? 'Warning' : 'Healthy'}
                </span>
              </div>
              <div className="health-value">{systemHealth.memory}%</div>
              <div className="health-bar">
                <div className="health-fill" style={{width: `${systemHealth.memory}%`}}></div>
              </div>
            </div>

            <div className="health-card">
              <div className="health-header">
                <h3>Disk Usage</h3>
                <span className={`health-status ${systemHealth.disk > 80 ? 'critical' : systemHealth.disk > 60 ? 'warning' : 'healthy'}`}>
                  {systemHealth.disk > 80 ? 'Critical' : systemHealth.disk > 60 ? 'Warning' : 'Healthy'}
                </span>
              </div>
              <div className="health-value">{systemHealth.disk}%</div>
              <div className="health-bar">
                <div className="health-fill" style={{width: `${systemHealth.disk}%`}}></div>
              </div>
            </div>

            <div className="health-card">
              <div className="health-header">
                <h3>Network I/O</h3>
                <span className={`health-status ${systemHealth.network > 80 ? 'critical' : systemHealth.network > 60 ? 'warning' : 'healthy'}`}>
                  {systemHealth.network > 80 ? 'Critical' : systemHealth.network > 60 ? 'Warning' : 'Healthy'}
                </span>
              </div>
              <div className="health-value">{systemHealth.network}%</div>
              <div className="health-bar">
                <div className="health-fill" style={{width: `${systemHealth.network}%`}}></div>
              </div>
            </div>
          </div>
        </div>

        {/* User Management */}
        <div className="user-management">
          <div className="section-header">
            <h2>User Management</h2>
            <button className="btn btn-primary">Add User</button>
          </div>
          <div className="users-table">
            <div className="table-header">
              <div className="table-cell">Name</div>
              <div className="table-cell">Email</div>
              <div className="table-cell">Role</div>
              <div className="table-cell">Status</div>
              <div className="table-cell">Last Login</div>
              <div className="table-cell">Actions</div>
            </div>
            <div className="table-row">
              <div className="table-cell">
                <div className="user-info">
                  <div className="user-avatar">JD</div>
                  <div className="user-details">
                    <div className="user-name">John Doe</div>
                    <div className="user-id">ID: 1001</div>
                  </div>
                </div>
              </div>
              <div className="table-cell">john.doe@nexus.com</div>
              <div className="table-cell">
                <span className="role-badge admin">Admin</span>
              </div>
              <div className="table-cell">
                <span className="status-badge active">Active</span>
              </div>
              <div className="table-cell">2 hours ago</div>
              <div className="table-cell">
                <div className="action-buttons">
                  <button className="btn btn-small">Edit</button>
                  <button className="btn btn-small btn-danger">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Service Management */}
        <div className="service-management">
          <h2>Service Management</h2>
          <div className="services-grid">
            <div className="service-card">
              <div className="service-header">
                <h3>API Gateway</h3>
                <span className="service-status running">Running</span>
              </div>
              <div className="service-metrics">
                <div className="metric">
                  <span className="metric-label">Uptime:</span>
                  <span className="metric-value">99.9%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Requests/min:</span>
                  <span className="metric-value">1,247</span>
                </div>
              </div>
              <div className="service-actions">
                <button className="btn btn-small">Restart</button>
                <button className="btn btn-small">Configure</button>
              </div>
            </div>

            <div className="service-card">
              <div className="service-header">
                <h3>Database</h3>
                <span className="service-status running">Running</span>
              </div>
              <div className="service-metrics">
                <div className="metric">
                  <span className="metric-label">Connections:</span>
                  <span className="metric-value">45/100</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Query Time:</span>
                  <span className="metric-value">12ms</span>
                </div>
              </div>
              <div className="service-actions">
                <button className="btn btn-small">Backup</button>
                <button className="btn btn-small">Optimize</button>
              </div>
            </div>

            <div className="service-card">
              <div className="service-header">
                <h3>AI Engine</h3>
                <span className="service-status warning">Warning</span>
              </div>
              <div className="service-metrics">
                <div className="metric">
                  <span className="metric-label">Memory:</span>
                  <span className="metric-value">85%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Queue:</span>
                  <span className="metric-value">23 tasks</span>
                </div>
              </div>
              <div className="service-actions">
                <button className="btn btn-small">Scale</button>
                <button className="btn btn-small">Monitor</button>
              </div>
            </div>
          </div>
        </div>

        {/* System Configuration */}
        <div className="system-configuration">
          <h2>System Configuration</h2>
          <div className="config-sections">
            <div className="config-section">
              <h3>Security Settings</h3>
              <div className="config-items">
                <div className="config-item">
                  <label>Two-Factor Authentication</label>
                  <div className="config-control">
                    <input type="checkbox" defaultChecked />
                    <span className="config-status">Enabled</span>
                  </div>
                </div>
                <div className="config-item">
                  <label>Session Timeout</label>
                  <div className="config-control">
                    <select defaultValue="30">
                      <option value="15">15 minutes</option>
                      <option value="30">30 minutes</option>
                      <option value="60">1 hour</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="config-section">
              <h3>Performance Settings</h3>
              <div className="config-items">
                <div className="config-item">
                  <label>Cache TTL</label>
                  <div className="config-control">
                    <input type="number" defaultValue="3600" />
                    <span className="config-unit">seconds</span>
                  </div>
                </div>
                <div className="config-item">
                  <label>Max Connections</label>
                  <div className="config-control">
                    <input type="number" defaultValue="100" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}