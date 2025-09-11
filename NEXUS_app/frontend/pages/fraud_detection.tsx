// NEXUS_app/frontend/pages/fraud-detection.tsx
import Layout from '../../components/Layout';
import { useState, useEffect } from 'react';

export default function FraudDetection() {
  const [transactions, setTransactions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [riskScore, setRiskScore] = useState(0);
  const [detectionRules, setDetectionRules] = useState([]);

  useEffect(() => {
    // Simulate real-time transaction monitoring
    const interval = setInterval(() => {
      const newTransaction = {
        id: Date.now(),
        amount: Math.floor(Math.random() * 10000),
        merchant: ['Amazon', 'Walmart', 'Target', 'Unknown Merchant'][Math.floor(Math.random() * 4)],
        location: ['New York', 'California', 'Texas', 'Unknown'][Math.floor(Math.random() * 4)],
        riskScore: Math.floor(Math.random() * 100),
        timestamp: new Date().toISOString(),
        status: Math.random() > 0.8 ? 'flagged' : 'approved'
      };
      
      setTransactions(prev => [newTransaction, ...prev.slice(0, 49)]);
      
      if (newTransaction.riskScore > 70) {
        setAlerts(prev => [{
          id: Date.now(),
          type: 'high_risk',
          message: `High-risk transaction detected: $${newTransaction.amount}`,
          timestamp: new Date().toISOString()
        }, ...prev.slice(0, 9)]);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Layout title="Fraud Detection" userRole="investigator">
      <div className="fraud-detection">
        {/* Real-time Monitoring Dashboard */}
        <div className="monitoring-dashboard">
          <h2>Real-time Transaction Monitoring</h2>
          <div className="monitoring-stats">
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <div className="stat-value">{transactions.length}</div>
                <div className="stat-label">Total Transactions</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">⚠️</div>
              <div className="stat-content">
                <div className="stat-value">{alerts.length}</div>
                <div className="stat-label">Active Alerts</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">🛡️</div>
              <div className="stat-content">
                <div className="stat-value">{transactions.filter(t => t.status === 'flagged').length}</div>
                <div className="stat-label">Blocked Transactions</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">💰</div>
              <div className="stat-content">
                <div className="stat-value">${transactions.reduce((sum, t) => sum + t.amount, 0).toLocaleString()}</div>
                <div className="stat-label">Total Volume</div>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Scoring */}
        <div className="risk-scoring">
          <h2>Risk Assessment</h2>
          <div className="risk-overview">
            <div className="risk-meter">
              <div className="risk-circle">
                <div className="risk-value">{riskScore}</div>
                <div className="risk-label">Risk Score</div>
              </div>
              <div className="risk-level">
                {riskScore > 80 ? 'Critical' : riskScore > 60 ? 'High' : riskScore > 40 ? 'Medium' : 'Low'}
              </div>
            </div>
            
            <div className="risk-factors">
              <h3>Risk Factors</h3>
              <div className="factors-list">
                <div className="factor-item">
                  <span className="factor-name">Unusual Amount</span>
                  <span className="factor-score">+15</span>
                </div>
                <div className="factor-item">
                  <span className="factor-name">New Merchant</span>
                  <span className="factor-score">+10</span>
                </div>
                <div className="factor-item">
                  <span className="factor-name">Geographic Anomaly</span>
                  <span className="factor-score">+20</span>
                </div>
                <div className="factor-item">
                  <span className="factor-name">Time Pattern</span>
                  <span className="factor-score">+5</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Transaction List */}
        <div className="transaction-monitoring">
          <h2>Transaction Monitoring</h2>
          <div className="transaction-filters">
            <select className="filter-select">
              <option value="all">All Transactions</option>
              <option value="flagged">Flagged Only</option>
              <option value="approved">Approved Only</option>
            </select>
            <input type="text" placeholder="Search transactions..." className="search-input" />
          </div>
          
          <div className="transactions-table">
            <div className="table-header">
              <div className="table-cell">Time</div>
              <div className="table-cell">Amount</div>
              <div className="table-cell">Merchant</div>
              <div className="table-cell">Location</div>
              <div className="table-cell">Risk Score</div>
              <div className="table-cell">Status</div>
              <div className="table-cell">Actions</div>
            </div>
            
            {transactions.slice(0, 20).map(transaction => (
              <div key={transaction.id} className={`table-row ${transaction.status === 'flagged' ? 'flagged' : ''}`}>
                <div className="table-cell">
                  {new Date(transaction.timestamp).toLocaleTimeString()}
                </div>
                <div className="table-cell">
                  ${transaction.amount.toLocaleString()}
                </div>
                <div className="table-cell">{transaction.merchant}</div>
                <div className="table-cell">{transaction.location}</div>
                <div className="table-cell">
                  <div className="risk-score">
                    <span className={`score ${transaction.riskScore > 70 ? 'high' : transaction.riskScore > 40 ? 'medium' : 'low'}`}>
                      {transaction.riskScore}
                    </span>
                  </div>
                </div>
                <div className="table-cell">
                  <span className={`status-badge ${transaction.status}`}>
                    {transaction.status}
                  </span>
                </div>
                <div className="table-cell">
                  <div className="action-buttons">
                    <button className="btn btn-small">Review</button>
                    <button className="btn btn-small">Block</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detection Rules */}
        <div className="detection-rules">
          <h2>Fraud Detection Rules</h2>
          <div className="rules-grid">
            <div className="rule-card">
              <div className="rule-header">
                <h3>Amount Threshold</h3>
                <span className="rule-status active">Active</span>
              </div>
              <div className="rule-description">
                Flag transactions over $5,000
              </div>
              <div className="rule-metrics">
                <div className="metric">
                  <span className="metric-label">Triggers:</span>
                  <span className="metric-value">23</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Accuracy:</span>
                  <span className="metric-value">87%</span>
                </div>
              </div>
            </div>
            
            <div className="rule-card">
              <div className="rule-header">
                <h3>Geographic Anomaly</h3>
                <span className="rule-status active">Active</span>
              </div>
              <div className="rule-description">
                Flag transactions from unusual locations
              </div>
              <div className="rule-metrics">
                <div className="metric">
                  <span className="metric-label">Triggers:</span>
                  <span className="metric-value">15</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Accuracy:</span>
                  <span className="metric-value">92%</span>
                </div>
              </div>
            </div>
            
            <div className="rule-card">
              <div className="rule-header">
                <h3>Velocity Check</h3>
                <span className="rule-status active">Active</span>
              </div>
              <div className="rule-description">
                Flag multiple transactions in short time
              </div>
              <div className="rule-metrics">
                <div className="metric">
                  <span className="metric-label">Triggers:</span>
                  <span className="metric-value">8</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Accuracy:</span>
                  <span className="metric-value">78%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Alert Management */}
        <div className="alert-management">
          <h2>Alert Management</h2>
          <div className="alerts-list">
            {alerts.map(alert => (
              <div key={alert.id} className={`alert-item ${alert.type}`}>
                <div className="alert-icon">
                  {alert.type === 'high_risk' ? '⚠️' : 'ℹ️'}
                </div>
                <div className="alert-content">
                  <div className="alert-message">{alert.message}</div>
                  <div className="alert-time">{new Date(alert.timestamp).toLocaleString()}</div>
                </div>
                <div className="alert-actions">
                  <button className="btn btn-small">Acknowledge</button>
                  <button className="btn btn-small">Investigate</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}