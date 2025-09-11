// NEXUS_app/frontend/pages/gdpr-compliance.tsx
import Layout from '../components/layout';
import { useState, useEffect } from 'react';

export default function GDPRCompliance() {
  const [dataRetentionPolicies, setDataRetentionPolicies] = useState([]);
  const [userConsent, setUserConsent] = useState([]);
  const [dataRequests, setDataRequests] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [complianceScore, setComplianceScore] = useState(0);

  useEffect(() => {
    // Simulate data loading
    const mockPolicies = [
      {
        id: 1,
        name: 'Transaction Data Retention',
        dataType: 'Financial Transactions',
        retentionPeriod: '7 years',
        legalBasis: 'Legal obligation',
        status: 'active',
        lastUpdated: '2024-01-15',
        affectedRecords: 15420
      },
      {
        id: 2,
        name: 'User Profile Data',
        dataType: 'Personal Information',
        retentionPeriod: '3 years',
        legalBasis: 'Consent',
        status: 'active',
        lastUpdated: '2024-01-10',
        affectedRecords: 892
      },
      {
        id: 3,
        name: 'Audit Logs',
        dataType: 'System Logs',
        retentionPeriod: '1 year',
        legalBasis: 'Legitimate interest',
        status: 'active',
        lastUpdated: '2024-01-12',
        affectedRecords: 45678
      },
      {
        id: 4,
        name: 'Marketing Data',
        dataType: 'Marketing Communications',
        retentionPeriod: '2 years',
        legalBasis: 'Consent',
        status: 'active',
        lastUpdated: '2024-01-08',
        affectedRecords: 234
      }
    ];

    const mockConsent = [
      {
        id: 1,
        userId: 'user_001',
        consentType: 'Data Processing',
        granted: true,
        grantedDate: '2024-01-15',
        expiresDate: '2025-01-15',
        purpose: 'Fraud detection and analysis',
        status: 'active'
      },
      {
        id: 2,
        userId: 'user_002',
        consentType: 'Marketing Communications',
        granted: false,
        grantedDate: null,
        expiresDate: null,
        purpose: 'Product updates and promotions',
        status: 'withdrawn'
      },
      {
        id: 3,
        userId: 'user_003',
        consentType: 'Data Sharing',
        granted: true,
        grantedDate: '2024-01-10',
        expiresDate: '2024-07-10',
        purpose: 'Third-party integrations',
        status: 'active'
      }
    ];

    const mockRequests = [
      {
        id: 1,
        userId: 'user_001',
        requestType: 'Data Access',
        status: 'completed',
        submittedDate: '2024-01-15',
        completedDate: '2024-01-16',
        dataProvided: 'Complete user profile and transaction history'
      },
      {
        id: 2,
        userId: 'user_002',
        requestType: 'Data Deletion',
        status: 'in_progress',
        submittedDate: '2024-01-14',
        completedDate: null,
        dataProvided: 'Partial deletion in progress'
      },
      {
        id: 3,
        userId: 'user_003',
        requestType: 'Data Portability',
        status: 'pending',
        submittedDate: '2024-01-16',
        completedDate: null,
        dataProvided: null
      }
    ];

    setDataRetentionPolicies(mockPolicies);
    setUserConsent(mockConsent);
    setDataRequests(mockRequests);
    setComplianceScore(87);
  }, []);

  const handleDataRetentionUpdate = (policyId, newPeriod) => {
    setDataRetentionPolicies(prev =>
      prev.map(policy =>
        policy.id === policyId
          ? { ...policy, retentionPeriod: newPeriod, lastUpdated: new Date().toISOString().split('T')[0] }
          : policy
      )
    );
  };

  const handleConsentUpdate = (consentId, granted) => {
    setUserConsent(prev =>
      prev.map(consent =>
        consent.id === consentId
          ? { 
              ...consent, 
              granted, 
              grantedDate: granted ? new Date().toISOString().split('T')[0] : null,
              status: granted ? 'active' : 'withdrawn'
            }
          : consent
      )
    );
  };

  const processDataRequest = (requestId) => {
    setDataRequests(prev =>
      prev.map(request =>
        request.id === requestId
          ? { 
              ...request, 
              status: 'completed', 
              completedDate: new Date().toISOString().split('T')[0],
              dataProvided: 'Data export completed successfully'
            }
          : request
      )
    );
  };

  return (
    <Layout title="GDPR Compliance" userRole="compliance">
      <div className="gdpr-compliance">
        {/* Header */}
        <div className="compliance-header">
          <h1>GDPR Compliance Dashboard</h1>
          <div className="compliance-score">
            <div className="score-circle">
              <div className="score-value">{complianceScore}%</div>
              <div className="score-label">Compliance Score</div>
            </div>
          </div>
        </div>

        {/* Compliance Overview */}
        <div className="compliance-overview">
          <div className="overview-cards">
            <div className="overview-card">
              <div className="card-icon">📋</div>
              <div className="card-content">
                <div className="card-value">{dataRetentionPolicies.length}</div>
                <div className="card-label">Active Policies</div>
              </div>
            </div>
            
            <div className="overview-card">
              <div className="card-icon">👥</div>
              <div className="card-content">
                <div className="card-value">{userConsent.length}</div>
                <div className="card-label">Consent Records</div>
              </div>
            </div>
            
            <div className="overview-card">
              <div className="card-icon">📝</div>
              <div className="card-content">
                <div className="card-value">{dataRequests.length}</div>
                <div className="card-label">Data Requests</div>
              </div>
            </div>
            
            <div className="overview-card">
              <div className="card-icon">⚠️</div>
              <div className="card-content">
                <div className="card-value">{dataRequests.filter(r => r.status === 'pending').length}</div>
                <div className="card-label">Pending Requests</div>
              </div>
            </div>
          </div>
        </div>

        {/* Data Retention Policies */}
        <div className="data-retention">
          <h2>Data Retention Policies</h2>
          <div className="policies-grid">
            {dataRetentionPolicies.map(policy => (
              <div key={policy.id} className="policy-card">
                <div className="policy-header">
                  <h3>{policy.name}</h3>
                  <span className={`status-badge ${policy.status}`}>{policy.status}</span>
                </div>
                
                <div className="policy-details">
                  <div className="detail-row">
                    <span className="detail-label">Data Type:</span>
                    <span className="detail-value">{policy.dataType}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Retention Period:</span>
                    <span className="detail-value">{policy.retentionPeriod}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Legal Basis:</span>
                    <span className="detail-value">{policy.legalBasis}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Affected Records:</span>
                    <span className="detail-value">{policy.affectedRecords.toLocaleString()}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">Last Updated:</span>
                    <span className="detail-value">{policy.lastUpdated}</span>
                  </div>
                </div>
                
                <div className="policy-actions">
                  <button className="btn btn-small">Edit Policy</button>
                  <button className="btn btn-small">View Records</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* User Consent Management */}
        <div className="consent-management">
          <h2>User Consent Management</h2>
          <div className="consent-filters">
            <select className="filter-select">
              <option value="all">All Consent Types</option>
              <option value="active">Active Only</option>
              <option value="withdrawn">Withdrawn Only</option>
            </select>
            <input type="text" placeholder="Search users..." className="search-input" />
          </div>
          
          <div className="consent-table">
            <div className="table-header">
              <div className="table-cell">User ID</div>
              <div className="table-cell">Consent Type</div>
              <div className="table-cell">Status</div>
              <div className="table-cell">Granted Date</div>
              <div className="table-cell">Expires Date</div>
              <div className="table-cell">Purpose</div>
              <div className="table-cell">Actions</div>
            </div>
            
            {userConsent.map(consent => (
              <div key={consent.id} className={`table-row ${consent.status}`}>
                <div className="table-cell">{consent.userId}</div>
                <div className="table-cell">{consent.consentType}</div>
                <div className="table-cell">
                  <span className={`status-badge ${consent.status}`}>
                    {consent.status}
                  </span>
                </div>
                <div className="table-cell">{consent.grantedDate || 'N/A'}</div>
                <div className="table-cell">{consent.expiresDate || 'N/A'}</div>
                <div className="table-cell">{consent.purpose}</div>
                <div className="table-cell">
                  <div className="action-buttons">
                    <button 
                      className="btn btn-small"
                      onClick={() => handleConsentUpdate(consent.id, !consent.granted)}
                    >
                      {consent.granted ? 'Withdraw' : 'Grant'}
                    </button>
                    <button className="btn btn-small">View Details</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data Subject Requests */}
        <div className="data-requests">
          <h2>Data Subject Requests</h2>
          <div className="requests-filters">
            <select className="filter-select">
              <option value="all">All Requests</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
            <select className="filter-select">
              <option value="all">All Types</option>
              <option value="Data Access">Data Access</option>
              <option value="Data Deletion">Data Deletion</option>
              <option value="Data Portability">Data Portability</option>
            </select>
          </div>
          
          <div className="requests-table">
            <div className="table-header">
              <div className="table-cell">Request ID</div>
              <div className="table-cell">User ID</div>
              <div className="table-cell">Request Type</div>
              <div className="table-cell">Status</div>
              <div className="table-cell">Submitted Date</div>
              <div className="table-cell">Completed Date</div>
              <div className="table-cell">Actions</div>
            </div>
            
            {dataRequests.map(request => (
              <div key={request.id} className={`table-row ${request.status}`}>
                <div className="table-cell">#{request.id}</div>
                <div className="table-cell">{request.userId}</div>
                <div className="table-cell">{request.requestType}</div>
                <div className="table-cell">
                  <span className={`status-badge ${request.status}`}>
                    {request.status}
                  </span>
                </div>
                <div className="table-cell">{request.submittedDate}</div>
                <div className="table-cell">{request.completedDate || 'N/A'}</div>
                <div className="table-cell">
                  <div className="action-buttons">
                    {request.status === 'pending' && (
                      <button 
                        className="btn btn-primary btn-small"
                        onClick={() => processDataRequest(request.id)}
                      >
                        Process
                      </button>
                    )}
                    <button className="btn btn-small">View Details</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Privacy Impact Assessment */}
        <div className="privacy-impact">
          <h2>Privacy Impact Assessment</h2>
          <div className="assessment-grid">
            <div className="assessment-card">
              <h3>Data Processing Activities</h3>
              <div className="activity-list">
                <div className="activity-item">
                  <span className="activity-name">Transaction Analysis</span>
                  <span className="activity-risk low">Low Risk</span>
                </div>
                <div className="activity-item">
                  <span className="activity-name">User Profiling</span>
                  <span className="activity-risk medium">Medium Risk</span>
                </div>
                <div className="activity-item">
                  <span className="activity-name">Data Sharing</span>
                  <span className="activity-risk high">High Risk</span>
                </div>
              </div>
            </div>
            
            <div className="assessment-card">
              <h3>Data Protection Measures</h3>
              <div className="measures-list">
                <div className="measure-item">
                  <span className="measure-name">Encryption at Rest</span>
                  <span className="measure-status implemented">✅ Implemented</span>
                </div>
                <div className="measure-item">
                  <span className="measure-name">Access Controls</span>
                  <span className="measure-status implemented">✅ Implemented</span>
                </div>
                <div className="measure-item">
                  <span className="measure-name">Data Minimization</span>
                  <span className="measure-status partial">⚠️ Partial</span>
                </div>
                <div className="measure-item">
                  <span className="measure-name">Regular Audits</span>
                  <span className="measure-status implemented">✅ Implemented</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Compliance Reports */}
        <div className="compliance-reports">
          <h2>Compliance Reports</h2>
          <div className="reports-grid">
            <div className="report-card">
              <h3>Monthly Compliance Report</h3>
              <p>Comprehensive overview of GDPR compliance status</p>
              <div className="report-actions">
                <button className="btn btn-primary">Generate Report</button>
                <button className="btn btn-secondary">Download PDF</button>
              </div>
            </div>
            
            <div className="report-card">
              <h3>Data Breach Report</h3>
              <p>Incident tracking and breach notification</p>
              <div className="report-actions">
                <button className="btn btn-primary">View Incidents</button>
                <button className="btn btn-secondary">Create Report</button>
              </div>
            </div>
            
            <div className="report-card">
              <h3>Consent Audit Report</h3>
              <p>User consent tracking and validation</p>
              <div className="report-actions">
                <button className="btn btn-primary">Run Audit</button>
                <button className="btn btn-secondary">Export Data</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
