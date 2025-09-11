import Layout from '../components/Layout';
import { useState } from 'react';
import Link from 'next/link';

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview');

  const features = [
    {
      title: 'AI-Powered Forensic Engine',
      description: 'Advanced AI models for pattern recognition and anomaly detection',
      icon: '🤖',
      link: '/guide/forensic-analysis'
    },
    {
      title: 'Fraud Detection & Prevention',
      description: 'Real-time threat detection with machine learning-based scoring',
      icon: '🛡️',
      link: '/guide/fraud-detection'
    },
    {
      title: 'Automated Reconciliation',
      description: 'Intelligent workflows for financial transaction reconciliation',
      icon: '🔄',
      link: '/guide/reconciliation'
    },
    {
      title: 'Evidence Management',
      description: 'Comprehensive tools for evidence analysis and case management',
      icon: '🔍',
      link: '/guide/evidence-management'
    },
    {
      title: 'Real-time Monitoring',
      description: 'Live dashboards and alerting systems',
      icon: '📊',
      link: '/dashboard'
    },
    {
      title: 'Enhanced Security Dashboard',
      description: 'Comprehensive security management with compliance monitoring, data encryption, and identity management',
      icon: '🔐',
      link: '/enhanced-security'
    }
  ];

  const userRoles = [
    {
      role: 'Investigator',
      description: 'Forensic analysis and evidence management',
      features: ['Case Management', 'Evidence Analysis', 'Report Generation'],
      link: '/guide/investigator'
    },
    {
      role: 'Compliance Officer',
      description: 'Regulatory compliance and risk assessment',
      features: ['Risk Scoring', 'Compliance Reports', 'Audit Trails'],
      link: '/guide/compliance'
    },
    {
      role: 'Executive',
      description: 'High-level overview and strategic insights',
      features: ['Executive Dashboard', 'Risk Overview', 'Performance Metrics'],
      link: '/guide/executive'
    }
  ];

  return (
    <Layout>
      <div className="hero-section">
        <h1 className="hero-title">🕵️ Nexus Forensic Platform</h1>
        <p className="hero-subtitle">
          Transform forensic investigations and compliance workflows with AI-powered intelligence
        </p>
        <div className="hero-actions">
          <Link href="/guide/quickstart" className="btn btn-primary">
            🚀 Get Started
          </Link>
          <Link href="/dashboard" className="btn btn-secondary">
            📊 View Dashboard
          </Link>
        </div>
      </div>

      <div className="tabs-container">
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={`tab ${activeTab === 'features' ? 'active' : ''}`}
            onClick={() => setActiveTab('features')}
          >
            Features
          </button>
          <button 
            className={`tab ${activeTab === 'roles' ? 'active' : ''}`}
            onClick={() => setActiveTab('roles')}
          >
            User Roles
          </button>
          <button 
            className={`tab ${activeTab === 'getting-started' ? 'active' : ''}`}
            onClick={() => setActiveTab('getting-started')}
          >
            Getting Started
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'overview' && (
            <div className="overview-content">
              <h2>Platform Overview</h2>
              <p>
                The Nexus Platform is a comprehensive forensic and reconciliation platform designed for 
                financial institutions and businesses that need robust, scalable solutions for compliance, 
                risk management, and operational efficiency.
              </p>
              
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-number">68%</div>
                  <div className="stat-label">Implementation Complete</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">25</div>
                  <div className="stat-label">Priority Tasks</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">17</div>
                  <div className="stat-label">Tasks Completed</div>
                </div>
                <div className="stat-card">
                  <div className="stat-number">8</div>
                  <div className="stat-label">Tasks Pending</div>
                </div>
              </div>

              <div className="architecture-preview">
                <h3>System Architecture</h3>
                <div className="architecture-diagram">
                  <div className="layer">
                    <div className="layer-title">Frontend Layer</div>
                    <div className="layer-components">
                      <span>Unified Dashboard</span>
                      <span>Fraud Graph</span>
                      <span>Risk Scores</span>
                      <span>Evidence Viewer</span>
                    </div>
                  </div>
                  <div className="layer">
                    <div className="layer-title">Gateway Layer</div>
                    <div className="layer-components">
                      <span>Reconciliation API</span>
                      <span>Fraud Graph API</span>
                      <span>Evidence API</span>
                      <span>Litigation API</span>
                    </div>
                  </div>
                  <div className="layer">
                    <div className="layer-title">AI Service Layer</div>
                    <div className="layer-components">
                      <span>Reconciliation Agent</span>
                      <span>Fraud Agent</span>
                      <span>Risk Agent</span>
                      <span>Evidence Agent</span>
                    </div>
                  </div>
                  <div className="layer">
                    <div className="layer-title">Datastore Layer</div>
                    <div className="layer-components">
                      <span>DuckDB OLAP</span>
                      <span>Neo4j Graph</span>
                      <span>PostgreSQL</span>
                      <span>Redis Cache</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'features' && (
            <div className="features-content">
              <h2>Platform Features</h2>
              <div className="features-grid">
                {features.map((feature, index) => (
                  <div key={index} className="feature-card">
                    <div className="feature-icon">{feature.icon}</div>
                    <h3 className="feature-title">{feature.title}</h3>
                    <p className="feature-description">{feature.description}</p>
                    <Link href={feature.link} className="feature-link">
                      Learn More →
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'roles' && (
            <div className="roles-content">
              <h2>User Roles & Capabilities</h2>
              <div className="roles-grid">
                {userRoles.map((role, index) => (
                  <div key={index} className="role-card">
                    <h3 className="role-title">{role.role}</h3>
                    <p className="role-description">{role.description}</p>
                    <ul className="role-features">
                      {role.features.map((feature, fIndex) => (
                        <li key={fIndex}>{feature}</li>
                      ))}
                    </ul>
                    <Link href={role.link} className="role-link">
                      Access {role.role} Portal →
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'getting-started' && (
            <div className="getting-started-content">
              <h2>Getting Started Guide</h2>
              
              <div className="steps-container">
                <div className="step">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h3>Choose Your Role</h3>
                    <p>Select your user role to access the appropriate interface and features.</p>
                    <div className="step-actions">
                      <Link href="/guide/role-selection" className="btn btn-small">
                        Select Role
                      </Link>
                    </div>
                  </div>
                </div>

                <div className="step">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h3>Complete Onboarding</h3>
                    <p>Go through the guided onboarding process to set up your workspace.</p>
                    <div className="step-actions">
                      <Link href="/guide/onboarding" className="btn btn-small">
                        Start Onboarding
                      </Link>
                    </div>
                  </div>
                </div>

                <div className="step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h3>Access Your Dashboard</h3>
                    <p>Navigate to your personalized dashboard to begin your work.</p>
                    <div className="step-actions">
                      <Link href="/dashboard" className="btn btn-small">
                        Go to Dashboard
                      </Link>
                    </div>
                  </div>
                </div>

                <div className="step">
                  <div className="step-number">4</div>
                  <div className="step-content">
                    <h3>Start Your First Task</h3>
                    <p>Begin with a guided task to familiarize yourself with the platform.</p>
                    <div className="step-actions">
                      <Link href="/guide/first-task" className="btn btn-small">
                        Start First Task
                      </Link>
                    </div>
                  </div>
                </div>
              </div>

              <div className="quick-actions">
                <h3>Quick Actions</h3>
                <div className="quick-actions-grid">
                  <Link href="/guide/quickstart" className="quick-action">
                    <span className="quick-action-icon">⚡</span>
                    <span className="quick-action-text">Quick Start Guide</span>
                  </Link>
                  <Link href="/guide/tutorials" className="quick-action">
                    <span className="quick-action-icon">📚</span>
                    <span className="quick-action-text">Video Tutorials</span>
                  </Link>
                  <Link href="/guide/faq" className="quick-action">
                    <span className="quick-action-icon">❓</span>
                    <span className="quick-action-text">FAQ</span>
                  </Link>
                  <Link href="/guide/support" className="quick-action">
                    <span className="quick-action-icon">🆘</span>
                    <span className="quick-action-text">Get Support</span>
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
