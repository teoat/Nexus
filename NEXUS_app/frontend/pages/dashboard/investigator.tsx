// NEXUS_app/frontend/pages/dashboard/investigator.tsx
import Layout from '../../components/Layout';
import { useState, useEffect } from 'react';

export default function InvestigatorDashboard() {
  const [cases, setCases] = useState([]);
  const [evidence, setEvidence] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);

  return (
    <Layout title="Investigator Dashboard" userRole="investigator">
      <div className="dashboard-grid">
        {/* Case Overview */}
        <div className="dashboard-section">
          <h2>Active Cases</h2>
          <div className="cases-grid">
            <div className="case-card">
              <div className="case-header">
                <h3>Case #2024-001</h3>
                <span className="case-status status-active">Active</span>
              </div>
              <p className="case-description">Financial fraud investigation</p>
              <div className="case-metrics">
                <div className="metric">
                  <span className="metric-label">Evidence Items:</span>
                  <span className="metric-value">47</span>
                </div>
                <div className="metric">
                  <span className="metric-label">AI Insights:</span>
                  <span className="metric-value">12</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Evidence Management */}
        <div className="dashboard-section">
          <h2>Evidence Queue</h2>
          <div className="evidence-list">
            <div className="evidence-item">
              <div className="evidence-icon">📄</div>
              <div className="evidence-info">
                <h4>Document_001.pdf</h4>
                <p>Processing... 85% complete</p>
              </div>
              <div className="evidence-status">
                <div className="progress-bar">
                  <div className="progress-fill" style={{width: '85%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Insights */}
        <div className="dashboard-section">
          <h2>AI-Powered Insights</h2>
          <div className="insights-panel">
            <div className="insight-card">
              <div className="insight-icon">🤖</div>
              <div className="insight-content">
                <h4>Pattern Detected</h4>
                <p>Unusual transaction pattern identified in Case #2024-001</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}