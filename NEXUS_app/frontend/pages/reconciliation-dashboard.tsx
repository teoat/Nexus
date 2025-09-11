// NEXUS_app/frontend/pages/reconciliation-dashboard.tsx
import Layout from '../components/layout';
import { useState, useEffect } from 'react';

export default function ReconciliationDashboard() {
  const [reconciliationJobs, setReconciliationJobs] = useState([]);
  const [financialData, setFinancialData] = useState([]);
  const [matchingResults, setMatchingResults] = useState([]);
  const [discrepancies, setDiscrepancies] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Simulate data loading
    const mockJobs = [
      {
        id: 1,
        name: 'Bank Statement Reconciliation',
        status: 'running',
        progress: 75,
        startTime: '2024-01-15 09:00:00',
        endTime: null,
        recordsProcessed: 1250,
        totalRecords: 1667,
        matches: 1100,
        discrepancies: 150
      },
      {
        id: 2,
        name: 'Credit Card Reconciliation',
        status: 'completed',
        progress: 100,
        startTime: '2024-01-15 08:30:00',
        endTime: '2024-01-15 10:15:00',
        recordsProcessed: 890,
        totalRecords: 890,
        matches: 845,
        discrepancies: 45
      },
      {
        id: 3,
        name: 'Vendor Payment Reconciliation',
        status: 'pending',
        progress: 0,
        startTime: null,
        endTime: null,
        recordsProcessed: 0,
        totalRecords: 2340,
        matches: 0,
        discrepancies: 0
      }
    ];

    const mockFinancialData = [
      {
        id: 1,
        source: 'Bank Statement',
        account: 'Main Checking',
        date: '2024-01-15',
        amount: 1500.00,
        description: 'Payment from Client ABC',
        reference: 'TXN-001',
        status: 'matched'
      },
      {
        id: 2,
        source: 'Internal Records',
        account: 'Main Checking',
        date: '2024-01-15',
        amount: 1500.00,
        description: 'Payment from Client ABC',
        reference: 'TXN-001',
        status: 'matched'
      },
      {
        id: 3,
        source: 'Bank Statement',
        account: 'Main Checking',
        date: '2024-01-14',
        amount: 2500.00,
        description: 'Payment from Client XYZ',
        reference: 'TXN-002',
        status: 'discrepancy'
      },
      {
        id: 4,
        source: 'Internal Records',
        account: 'Main Checking',
        date: '2024-01-14',
        amount: 2500.50,
        description: 'Payment from Client XYZ',
        reference: 'TXN-002',
        status: 'discrepancy'
      }
    ];

    setReconciliationJobs(mockJobs);
    setFinancialData(mockFinancialData);
  }, []);

  const startReconciliation = (jobId) => {
    setLoading(true);
    // Simulate starting reconciliation job
    setTimeout(() => {
      setReconciliationJobs(prev => 
        prev.map(job => 
          job.id === jobId 
            ? { ...job, status: 'running', startTime: new Date().toISOString() }
            : job
        )
      );
      setLoading(false);
    }, 1000);
  };

  const stopReconciliation = (jobId) => {
    setReconciliationJobs(prev => 
      prev.map(job => 
        job.id === jobId 
          ? { ...job, status: 'stopped', endTime: new Date().toISOString() }
          : job
      )
    );
  };

  return (
    <Layout title="Reconciliation Dashboard" userRole="compliance">
      <div className="reconciliation-dashboard">
        {/* Header */}
        <div className="dashboard-header">
          <h1>Financial Data Reconciliation</h1>
          <div className="header-actions">
            <button className="btn btn-primary">New Reconciliation Job</button>
            <button className="btn btn-secondary">Import Data</button>
            <button className="btn btn-secondary">Export Results</button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-icon">🔄</div>
            <div className="card-content">
              <div className="card-value">{reconciliationJobs.length}</div>
              <div className="card-label">Total Jobs</div>
            </div>
          </div>
          
          <div className="summary-card">
            <div className="card-icon">✅</div>
            <div className="card-content">
              <div className="card-value">{reconciliationJobs.filter(j => j.status === 'completed').length}</div>
              <div className="card-label">Completed</div>
            </div>
          </div>
          
          <div className="summary-card">
            <div className="card-icon">⚠️</div>
            <div className="card-content">
              <div className="card-value">{reconciliationJobs.reduce((sum, j) => sum + j.discrepancies, 0)}</div>
              <div className="card-label">Discrepancies</div>
            </div>
          </div>
          
          <div className="summary-card">
            <div className="card-icon">📊</div>
            <div className="card-content">
              <div className="card-value">{reconciliationJobs.reduce((sum, j) => sum + j.recordsProcessed, 0)}</div>
              <div className="card-label">Records Processed</div>
            </div>
          </div>
        </div>

        {/* Reconciliation Jobs */}
        <div className="reconciliation-jobs">
          <h2>Reconciliation Jobs</h2>
          <div className="jobs-grid">
            {reconciliationJobs.map(job => (
              <div key={job.id} className={`job-card ${job.status}`}>
                <div className="job-header">
                  <h3>{job.name}</h3>
                  <span className={`status-badge ${job.status}`}>{job.status}</span>
                </div>
                
                <div className="job-progress">
                  <div className="progress-header">
                    <span>Progress</span>
                    <span>{job.progress}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{width: `${job.progress}%`}}
                    ></div>
                  </div>
                </div>
                
                <div className="job-metrics">
                  <div className="metric">
                    <span className="metric-label">Records:</span>
                    <span className="metric-value">{job.recordsProcessed}/{job.totalRecords}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Matches:</span>
                    <span className="metric-value">{job.matches}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Discrepancies:</span>
                    <span className="metric-value">{job.discrepancies}</span>
                  </div>
                </div>
                
                <div className="job-actions">
                  {job.status === 'pending' && (
                    <button 
                      className="btn btn-primary btn-small"
                      onClick={() => startReconciliation(job.id)}
                      disabled={loading}
                    >
                      Start
                    </button>
                  )}
                  {job.status === 'running' && (
                    <button 
                      className="btn btn-danger btn-small"
                      onClick={() => stopReconciliation(job.id)}
                    >
                      Stop
                    </button>
                  )}
                  <button className="btn btn-secondary btn-small">View Details</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Financial Data Table */}
        <div className="financial-data">
          <h2>Financial Data</h2>
          <div className="data-filters">
            <select className="filter-select">
              <option value="all">All Records</option>
              <option value="matched">Matched Only</option>
              <option value="discrepancy">Discrepancies Only</option>
              <option value="unmatched">Unmatched Only</option>
            </select>
            <input type="text" placeholder="Search records..." className="search-input" />
          </div>
          
          <div className="data-table">
            <div className="table-header">
              <div className="table-cell">Source</div>
              <div className="table-cell">Account</div>
              <div className="table-cell">Date</div>
              <div className="table-cell">Amount</div>
              <div className="table-cell">Description</div>
              <div className="table-cell">Reference</div>
              <div className="table-cell">Status</div>
              <div className="table-cell">Actions</div>
            </div>
            
            {financialData.map(record => (
              <div key={record.id} className={`table-row ${record.status}`}>
                <div className="table-cell">{record.source}</div>
                <div className="table-cell">{record.account}</div>
                <div className="table-cell">{record.date}</div>
                <div className="table-cell">${record.amount.toFixed(2)}</div>
                <div className="table-cell">{record.description}</div>
                <div className="table-cell">{record.reference}</div>
                <div className="table-cell">
                  <span className={`status-badge ${record.status}`}>
                    {record.status}
                  </span>
                </div>
                <div className="table-cell">
                  <div className="action-buttons">
                    <button className="btn btn-small">Match</button>
                    <button className="btn btn-small">Flag</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Discrepancy Analysis */}
        <div className="discrepancy-analysis">
          <h2>Discrepancy Analysis</h2>
          <div className="discrepancy-charts">
            <div className="chart-card">
              <h3>Discrepancy Types</h3>
              <div className="chart-placeholder">
                <div className="chart-bar" style={{height: '60%'}}>
                  <span>Amount Mismatch</span>
                </div>
                <div className="chart-bar" style={{height: '40%'}}>
                  <span>Missing Records</span>
                </div>
                <div className="chart-bar" style={{height: '30%'}}>
                  <span>Date Mismatch</span>
                </div>
                <div className="chart-bar" style={{height: '20%'}}>
                  <span>Reference Mismatch</span>
                </div>
              </div>
            </div>
            
            <div className="chart-card">
              <h3>Reconciliation Trends</h3>
              <div className="trend-chart">
                <div className="trend-line">
                  <div className="trend-point" style={{left: '10%', top: '80%'}}></div>
                  <div className="trend-point" style={{left: '30%', top: '70%'}}></div>
                  <div className="trend-point" style={{left: '50%', top: '60%'}}></div>
                  <div className="trend-point" style={{left: '70%', top: '50%'}}></div>
                  <div className="trend-point" style={{left: '90%', top: '40%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Matching Rules */}
        <div className="matching-rules">
          <h2>Matching Rules</h2>
          <div className="rules-grid">
            <div className="rule-card">
              <h3>Amount Matching</h3>
              <p>Match records with identical amounts within tolerance</p>
              <div className="rule-settings">
                <label>
                  <input type="checkbox" defaultChecked />
                  Enable amount matching
                </label>
                <label>
                  Tolerance: <input type="number" defaultValue="0.01" step="0.01" />
                </label>
              </div>
            </div>
            
            <div className="rule-card">
              <h3>Date Matching</h3>
              <p>Match records within date range</p>
              <div className="rule-settings">
                <label>
                  <input type="checkbox" defaultChecked />
                  Enable date matching
                </label>
                <label>
                  Date range: <input type="number" defaultValue="3" /> days
                </label>
              </div>
            </div>
            
            <div className="rule-card">
              <h3>Reference Matching</h3>
              <p>Match records with identical reference numbers</p>
              <div className="rule-settings">
                <label>
                  <input type="checkbox" defaultChecked />
                  Enable reference matching
                </label>
                <label>
                  <input type="checkbox" defaultChecked />
                  Case sensitive
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
