'use client';
import Layout from '../components/Layout';
import { useState, useEffect } from 'react';
import Link from 'next/link';

interface ReconciliationJob {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'requires_human_judgment' | 'escalated';
  source_system: string;
  target_system: string;
  data_type: string;
  total_records: number;
  matched_records: number;
  unmatched_records: number;
  discrepancy_count: number;
  confidence_score: number;
  created_at: string;
  completed_at?: string;
}

interface Discrepancy {
  id: string;
  job_id: string;
  discrepancy_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  source_record_id?: string;
  target_record_id?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
}

interface HumanJudgment {
  id: string;
  job_id: string;
  discrepancy_id?: string;
  judgment_type: string;
  status: 'pending' | 'in_review' | 'approved' | 'rejected' | 'escalated';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  title: string;
  description: string;
  assigned_to?: string;
  created_at: string;
  reviewed_at?: string;
}

interface ReconciliationSummary {
  total_jobs: number;
  active_jobs: number;
  completed_jobs: number;
  total_discrepancies: number;
  pending_judgments: number;
  urgent_judgments: number;
  overall_health: number;
}

export default function ReconciliationDashboard() {
  const [activeView, setActiveView] = useState('overview');
  const [jobs, setJobs] = useState<ReconciliationJob[]>([]);
  const [discrepancies, setDiscrepancies] = useState<Discrepancy[]>([]);
  const [judgments, setJudgments] = useState<HumanJudgment[]>([]);
  const [summary, setSummary] = useState<ReconciliationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<string | null>(null);

  // Mock data for demonstration
  useEffect(() => {
    const mockJobs: ReconciliationJob[] = [
      {
        id: '1',
        name: 'Daily Transaction Reconciliation',
        description: 'Reconcile daily transactions between payment gateway and accounting system',
        status: 'completed',
        source_system: 'Payment Gateway',
        target_system: 'Accounting System',
        data_type: 'transactions',
        total_records: 15420,
        matched_records: 15350,
        unmatched_records: 70,
        discrepancy_count: 15,
        confidence_score: 0.95,
        created_at: '2024-01-15T08:00:00Z',
        completed_at: '2024-01-15T10:30:00Z'
      },
      {
        id: '2',
        name: 'User Account Synchronization',
        description: 'Sync user accounts between CRM and user management system',
        status: 'requires_human_judgment',
        source_system: 'CRM System',
        target_system: 'User Management',
        data_type: 'users',
        total_records: 5420,
        matched_records: 5200,
        unmatched_records: 220,
        discrepancy_count: 45,
        confidence_score: 0.78,
        created_at: '2024-01-15T09:00:00Z'
      },
      {
        id: '3',
        name: 'Inventory Level Reconciliation',
        description: 'Reconcile inventory levels between warehouse and e-commerce system',
        status: 'in_progress',
        source_system: 'Warehouse Management',
        target_system: 'E-commerce Platform',
        data_type: 'inventory',
        total_records: 12500,
        matched_records: 8500,
        unmatched_records: 4000,
        discrepancy_count: 0,
        confidence_score: 0.0,
        created_at: '2024-01-15T10:00:00Z'
      }
    ];

    const mockDiscrepancies: Discrepancy[] = [
      {
        id: '1',
        job_id: '2',
        discrepancy_type: 'mismatch',
        severity: 'high',
        description: 'User email mismatch between systems',
        source_record_id: 'user_123',
        target_record_id: 'user_456',
        status: 'pending',
        created_at: '2024-01-15T09:15:00Z'
      },
      {
        id: '2',
        job_id: '2',
        discrepancy_type: 'missing_in_target',
        severity: 'medium',
        description: 'User exists in CRM but not in user management',
        source_record_id: 'user_789',
        status: 'pending',
        created_at: '2024-01-15T09:20:00Z'
      }
    ];

    const mockJudgments: HumanJudgment[] = [
      {
        id: '1',
        job_id: '2',
        discrepancy_id: '1',
        judgment_type: 'data_correction',
        status: 'pending',
        priority: 'high',
        title: 'Email Address Mismatch Resolution',
        description: 'Determine correct email address for user_123',
        assigned_to: 'user_456',
        created_at: '2024-01-15T09:30:00Z'
      },
      {
        id: '2',
        job_id: '2',
        discrepancy_id: '2',
        judgment_type: 'user_creation',
        status: 'in_review',
        priority: 'medium',
        title: 'Create Missing User Account',
        description: 'Create user account in user management system',
        assigned_to: 'user_789',
        created_at: '2024-01-15T09:35:00Z'
      }
    ];

    const mockSummary: ReconciliationSummary = {
      total_jobs: 3,
      active_jobs: 2,
      completed_jobs: 1,
      total_discrepancies: 2,
      pending_judgments: 1,
      urgent_judgments: 1,
      overall_health: 85
    };

    setTimeout(() => {
      setJobs(mockJobs);
      setDiscrepancies(mockDiscrepancies);
      setJudgments(mockJudgments);
      setSummary(mockSummary);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      case 'requires_human_judgment': return 'text-yellow-600 bg-yellow-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'escalated': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading reconciliation dashboard...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="reconciliation-header">
        <h1>🔄 Reconciliation & Human Judgment Dashboard</h1>
        <p className="reconciliation-subtitle">
          Monitor data reconciliation processes and manage human judgment workflows
        </p>
      </div>

      <div className="reconciliation-navigation">
        <button 
          className={`nav-btn ${activeView === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveView('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`nav-btn ${activeView === 'jobs' ? 'active' : ''}`}
          onClick={() => setActiveView('jobs')}
        >
          🔄 Jobs
        </button>
        <button 
          className={`nav-btn ${activeView === 'discrepancies' ? 'active' : ''}`}
          onClick={() => setActiveView('discrepancies')}
        >
          ⚠️ Discrepancies
        </button>
        <button 
          className={`nav-btn ${activeView === 'judgments' ? 'active' : ''}`}
          onClick={() => setActiveView('judgments')}
        >
          👥 Human Judgments
        </button>
        <button 
          className={`nav-btn ${activeView === 'rules' ? 'active' : ''}`}
          onClick={() => setActiveView('rules')}
        >
          ⚙️ Rules
        </button>
      </div>

      <div className="reconciliation-content">
        {activeView === 'overview' && (
          <div className="overview-section">
            <div className="summary-cards">
              <div className="summary-card">
                <h3>Total Jobs</h3>
                <div className="summary-value">{summary?.total_jobs}</div>
                <div className="summary-detail">Active: {summary?.active_jobs}</div>
              </div>
              <div className="summary-card">
                <h3>Discrepancies</h3>
                <div className="summary-value">{summary?.total_discrepancies}</div>
                <div className="summary-detail">Pending: {summary?.pending_judgments}</div>
              </div>
              <div className="summary-card">
                <h3>Human Judgments</h3>
                <div className="summary-value">{summary?.pending_judgments}</div>
                <div className="summary-detail">Urgent: {summary?.urgent_judgments}</div>
              </div>
              <div className="summary-card">
                <h3>System Health</h3>
                <div className="summary-value">{summary?.overall_health}%</div>
                <div className="summary-detail">Overall Status</div>
              </div>
            </div>

            <div className="recent-activity">
              <h3>Recent Activity</h3>
              <div className="activity-list">
                {jobs.slice(0, 5).map(job => (
                  <div key={job.id} className="activity-item">
                    <div className="activity-icon">🔄</div>
                    <div className="activity-content">
                      <div className="activity-title">{job.name}</div>
                      <div className="activity-description">
                        {job.source_system} → {job.target_system}
                      </div>
                      <div className="activity-time">
                        {new Date(job.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div className={`activity-status ${getStatusColor(job.status)}`}>
                      {job.status.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeView === 'jobs' && (
          <div className="jobs-section">
            <div className="section-header">
              <h3>Reconciliation Jobs</h3>
              <button className="btn-primary">Create New Job</button>
            </div>
            
            <div className="jobs-table">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Source → Target</th>
                    <th>Records</th>
                    <th>Discrepancies</th>
                    <th>Confidence</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map(job => (
                    <tr key={job.id}>
                      <td>
                        <div className="job-name">{job.name}</div>
                        <div className="job-description">{job.description}</div>
                      </td>
                      <td>
                        <span className={`status-badge ${getStatusColor(job.status)}`}>
                          {job.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>
                        <div className="system-flow">
                          {job.source_system} → {job.target_system}
                        </div>
                        <div className="data-type">{job.data_type}</div>
                      </td>
                      <td>
                        <div className="record-stats">
                          <div>Total: {job.total_records.toLocaleString()}</div>
                          <div>Matched: {job.matched_records.toLocaleString()}</div>
                          <div>Unmatched: {job.unmatched_records.toLocaleString()}</div>
                        </div>
                      </td>
                      <td>
                        <div className="discrepancy-count">
                          {job.discrepancy_count}
                        </div>
                      </td>
                      <td>
                        <div className="confidence-score">
                          {(job.confidence_score * 100).toFixed(1)}%
                        </div>
                      </td>
                      <td>
                        <div className="created-time">
                          {new Date(job.created_at).toLocaleDateString()}
                        </div>
                      </td>
                      <td>
                        <div className="action-buttons">
                          <button className="btn-small">View</button>
                          <button className="btn-small">Edit</button>
                          {job.status === 'requires_human_judgment' && (
                            <button className="btn-small btn-warning">Review</button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeView === 'discrepancies' && (
          <div className="discrepancies-section">
            <div className="section-header">
              <h3>Data Discrepancies</h3>
              <div className="filter-controls">
                <select>
                  <option>All Severities</option>
                  <option>Critical</option>
                  <option>High</option>
                  <option>Medium</option>
                  <option>Low</option>
                </select>
                <select>
                  <option>All Jobs</option>
                  {jobs.map(job => (
                    <option key={job.id} value={job.id}>{job.name}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="discrepancies-list">
              {discrepancies.map(discrepancy => (
                <div key={discrepancy.id} className="discrepancy-card">
                  <div className="discrepancy-header">
                    <div className="discrepancy-title">
                      <h4>{discrepancy.description}</h4>
                      <span className={`severity-badge ${getSeverityColor(discrepancy.severity)}`}>
                        {discrepancy.severity}
                      </span>
                    </div>
                    <div className="discrepancy-meta">
                      <span className="discrepancy-type">{discrepancy.discrepancy_type}</span>
                      <span className="discrepancy-time">
                        {new Date(discrepancy.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  
                  <div className="discrepancy-details">
                    <div className="record-ids">
                      {discrepancy.source_record_id && (
                        <div className="record-id">
                          <strong>Source:</strong> {discrepancy.source_record_id}
                        </div>
                      )}
                      {discrepancy.target_record_id && (
                        <div className="record-id">
                          <strong>Target:</strong> {discrepancy.target_record_id}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="discrepancy-actions">
                    <button className="btn-small">View Details</button>
                    <button className="btn-small btn-primary">Resolve</button>
                    <button className="btn-small btn-warning">Request Judgment</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeView === 'judgments' && (
          <div className="judgments-section">
            <div className="section-header">
              <h3>Human Judgment Requests</h3>
              <div className="filter-controls">
                <select>
                  <option>All Statuses</option>
                  <option>Pending</option>
                  <option>In Review</option>
                  <option>Approved</option>
                  <option>Rejected</option>
                  <option>Escalated</option>
                </select>
                <select>
                  <option>All Priorities</option>
                  <option>Urgent</option>
                  <option>High</option>
                  <option>Medium</option>
                  <option>Low</option>
                </select>
              </div>
            </div>
            
            <div className="judgments-list">
              {judgments.map(judgment => (
                <div key={judgment.id} className="judgment-card">
                  <div className="judgment-header">
                    <div className="judgment-title">
                      <h4>{judgment.title}</h4>
                      <div className="judgment-badges">
                        <span className={`priority-badge ${getPriorityColor(judgment.priority)}`}>
                          {judgment.priority}
                        </span>
                        <span className={`status-badge ${getStatusColor(judgment.status)}`}>
                          {judgment.status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    <div className="judgment-meta">
                      <div className="judgment-type">{judgment.judgment_type}</div>
                      <div className="judgment-time">
                        {new Date(judgment.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  
                  <div className="judgment-content">
                    <p>{judgment.description}</p>
                    {judgment.assigned_to && (
                      <div className="assigned-to">
                        <strong>Assigned to:</strong> User {judgment.assigned_to}
                      </div>
                    )}
                  </div>
                  
                  <div className="judgment-actions">
                    <button className="btn-small">View Details</button>
                    {judgment.status === 'pending' && (
                      <button className="btn-small btn-primary">Start Review</button>
                    )}
                    {judgment.status === 'in_review' && (
                      <button className="btn-small btn-success">Submit Decision</button>
                    )}
                    <button className="btn-small btn-warning">Escalate</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeView === 'rules' && (
          <div className="rules-section">
            <div className="section-header">
              <h3>Reconciliation Rules</h3>
              <button className="btn-primary">Create New Rule</button>
            </div>
            
            <div className="rules-content">
              <div className="rules-info">
                <h4>Configure Automated Reconciliation Rules</h4>
                <p>
                  Set up rules to automatically match and reconcile data between systems.
                  Rules define matching criteria, tolerance thresholds, and escalation policies.
                </p>
              </div>
              
              <div className="rules-list">
                <div className="rule-card">
                  <div className="rule-header">
                    <h5>Transaction Matching Rule</h5>
                    <span className="rule-status active">Active</span>
                  </div>
                  <div className="rule-details">
                    <p><strong>Source:</strong> Payment Gateway</p>
                    <p><strong>Target:</strong> Accounting System</p>
                    <p><strong>Matching:</strong> Transaction ID + Amount + Date</p>
                    <p><strong>Tolerance:</strong> 0.01 (1 cent)</p>
                  </div>
                  <div className="rule-actions">
                    <button className="btn-small">Edit</button>
                    <button className="btn-small btn-danger">Disable</button>
                  </div>
                </div>
                
                <div className="rule-card">
                  <div className="rule-header">
                    <h5>User Account Matching Rule</h5>
                    <span className="rule-status active">Active</span>
                  </div>
                  <div className="rule-details">
                    <p><strong>Source:</strong> CRM System</p>
                    <p><strong>Target:</strong> User Management</p>
                    <p><strong>Matching:</strong> Email Address (Fuzzy)</p>
                    <p><strong>Tolerance:</strong> 0.85 (85% similarity)</p>
                  </div>
                  <div className="rule-actions">
                    <button className="btn-small">Edit</button>
                    <button className="btn-small btn-danger">Disable</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .reconciliation-header {
          margin-bottom: 2rem;
        }
        
        .reconciliation-header h1 {
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
          color: #1f2937;
        }
        
        .reconciliation-subtitle {
          font-size: 1.1rem;
          color: #6b7280;
          margin: 0;
        }
        
        .reconciliation-navigation {
          display: flex;
          gap: 1rem;
          margin-bottom: 2rem;
          border-bottom: 1px solid #e5e7eb;
          padding-bottom: 1rem;
        }
        
        .nav-btn {
          padding: 0.75rem 1.5rem;
          border: none;
          background: #f9fafb;
          color: #374151;
          border-radius: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
          font-weight: 500;
        }
        
        .nav-btn:hover {
          background: #e5e7eb;
        }
        
        .nav-btn.active {
          background: #3b82f6;
          color: white;
        }
        
        .summary-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .summary-card {
          background: white;
          padding: 1.5rem;
          border-radius: 0.75rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          border: 1px solid #e5e7eb;
        }
        
        .summary-card h3 {
          margin: 0 0 0.5rem 0;
          color: #6b7280;
          font-size: 0.875rem;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        
        .summary-value {
          font-size: 2.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.25rem;
        }
        
        .summary-detail {
          color: #6b7280;
          font-size: 0.875rem;
        }
        
        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }
        
        .section-header h3 {
          margin: 0;
          color: #1f2937;
        }
        
        .btn-primary {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 0.5rem;
          cursor: pointer;
          font-weight: 500;
          transition: background 0.2s;
        }
        
        .btn-primary:hover {
          background: #2563eb;
        }
        
        .btn-small {
          padding: 0.5rem 1rem;
          border: 1px solid #d1d5db;
          background: white;
          color: #374151;
          border-radius: 0.375rem;
          cursor: pointer;
          font-size: 0.875rem;
          margin-right: 0.5rem;
          transition: all 0.2s;
        }
        
        .btn-small:hover {
          background: #f9fafb;
        }
        
        .btn-warning {
          background: #f59e0b;
          color: white;
          border-color: #f59e0b;
        }
        
        .btn-warning:hover {
          background: #d97706;
        }
        
        .btn-success {
          background: #10b981;
          color: white;
          border-color: #10b981;
        }
        
        .btn-success:hover {
          background: #059669;
        }
        
        .btn-danger {
          background: #ef4444;
          color: white;
          border-color: #ef4444;
        }
        
        .btn-danger:hover {
          background: #dc2626;
        }
        
        .status-badge, .severity-badge, .priority-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        
        .jobs-table {
          background: white;
          border-radius: 0.75rem;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .jobs-table table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .jobs-table th {
          background: #f9fafb;
          padding: 1rem;
          text-align: left;
          font-weight: 600;
          color: #374151;
          border-bottom: 1px solid #e5e7eb;
        }
        
        .jobs-table td {
          padding: 1rem;
          border-bottom: 1px solid #f3f4f6;
        }
        
        .job-name {
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 0.25rem;
        }
        
        .job-description {
          color: #6b7280;
          font-size: 0.875rem;
        }
        
        .system-flow {
          font-weight: 500;
          color: #1f2937;
        }
        
        .data-type {
          color: #6b7280;
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        
        .record-stats {
          font-size: 0.875rem;
          color: #374151;
        }
        
        .discrepancy-count {
          font-weight: 600;
          color: #dc2626;
        }
        
        .confidence-score {
          font-weight: 600;
          color: #059669;
        }
        
        .action-buttons {
          display: flex;
          gap: 0.5rem;
        }
        
        .discrepancies-list, .judgments-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .discrepancy-card, .judgment-card, .rule-card {
          background: white;
          padding: 1.5rem;
          border-radius: 0.75rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          border: 1px solid #e5e7eb;
        }
        
        .discrepancy-header, .judgment-header, .rule-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1rem;
        }
        
        .discrepancy-title, .judgment-title {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .discrepancy-title h4, .judgment-title h4 {
          margin: 0;
          color: #1f2937;
        }
        
        .discrepancy-badges, .judgment-badges {
          display: flex;
          gap: 0.5rem;
        }
        
        .discrepancy-meta, .judgment-meta {
          text-align: right;
          color: #6b7280;
          font-size: 0.875rem;
        }
        
        .discrepancy-details, .judgment-content {
          margin-bottom: 1rem;
        }
        
        .record-ids {
          display: flex;
          gap: 1rem;
          margin-top: 0.5rem;
        }
        
        .record-id {
          font-size: 0.875rem;
          color: #374151;
        }
        
        .discrepancy-actions, .judgment-actions, .rule-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .filter-controls {
          display: flex;
          gap: 1rem;
        }
        
        .filter-controls select {
          padding: 0.5rem;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          background: white;
        }
        
        .rules-content {
          background: white;
          padding: 1.5rem;
          border-radius: 0.75rem;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        .rules-info {
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #e5e7eb;
        }
        
        .rules-info h4 {
          margin: 0 0 0.5rem 0;
          color: #1f2937;
        }
        
        .rules-info p {
          margin: 0;
          color: #6b7280;
        }
        
        .rules-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .rule-status {
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
        .rule-status.active {
          background: #dcfce7;
          color: #166534;
        }
        
        .rule-details {
          margin: 1rem 0;
        }
        
        .rule-details p {
          margin: 0.25rem 0;
          color: #374151;
          font-size: 0.875rem;
        }
        
        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 400px;
        }
        
        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f4f6;
          border-top: 4px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-bottom: 1rem;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </Layout>
  );
}
