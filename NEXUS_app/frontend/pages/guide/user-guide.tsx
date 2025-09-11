import Layout from '../../components/Layout';
import Link from 'next/link';

export default function UserGuide() {
  const userRoles = [
    {
      title: 'Investigator',
      description: 'Forensic analysis and fraud detection specialists',
      icon: '🔍',
      responsibilities: [
        'Conduct forensic investigations',
        'Analyze suspicious transactions',
        'Generate investigation reports',
        'Manage case files and evidence'
      ],
      access: ['Fraud Detection', 'Forensic Analysis', 'Case Management', 'Reporting']
    },
    {
      title: 'Compliance Officer',
      description: 'Regulatory compliance and risk management',
      icon: '📋',
      responsibilities: [
        'Monitor regulatory compliance',
        'Assess risk levels',
        'Review and approve transactions',
        'Maintain compliance records'
      ],
      access: ['Compliance Monitoring', 'Risk Assessment', 'Transaction Review', 'Audit Trails']
    },
    {
      title: 'Financial Analyst',
      description: 'Financial data analysis and reconciliation',
      icon: '💰',
      responsibilities: [
        'Perform financial reconciliation',
        'Analyze transaction patterns',
        'Generate financial reports',
        'Monitor account balances'
      ],
      access: ['Reconciliation', 'Financial Analysis', 'Reporting', 'Account Monitoring']
    },
    {
      title: 'System Administrator',
      description: 'Platform configuration and user management',
      icon: '⚙️',
      responsibilities: [
        'Manage user accounts and permissions',
        'Configure system settings',
        'Monitor system performance',
        'Maintain system security'
      ],
      access: ['User Management', 'System Configuration', 'Performance Monitoring', 'Security Settings']
    }
  ];

  const platformFeatures = [
    {
      title: 'Fraud Detection',
      description: 'AI-powered fraud detection with real-time alerts',
      icon: '🛡️',
      details: [
        'Machine learning-based anomaly detection',
        'Real-time transaction monitoring',
        'Risk scoring and alerting',
        'Pattern recognition and analysis'
      ]
    },
    {
      title: 'Forensic Analysis',
      description: 'Comprehensive digital forensic investigation tools',
      icon: '🔬',
      details: [
        'Digital evidence collection',
        'Timeline analysis',
        'Data correlation and linking',
        'Investigation workflow management'
      ]
    },
    {
      title: 'Reconciliation',
      description: 'Automated financial reconciliation processes',
      icon: '🔄',
      details: [
        'Multi-source data matching',
        'Exception identification',
        'Automated reconciliation rules',
        'Audit trail maintenance'
      ]
    },
    {
      title: 'Reporting & Analytics',
      description: 'Comprehensive reporting and data visualization',
      icon: '📊',
      details: [
        'Custom report generation',
        'Interactive dashboards',
        'Data export capabilities',
        'Trend analysis and insights'
      ]
    }
  ];

  const commonTasks = [
    {
      title: 'Starting an Investigation',
      description: 'How to initiate a new forensic investigation',
      steps: [
        'Navigate to Case Management',
        'Click "New Case" button',
        'Fill in case details and assign investigators',
        'Upload initial evidence and documents',
        'Set investigation priorities and deadlines'
      ],
      tips: [
        'Always document the initial complaint or trigger',
        'Assign appropriate access permissions to team members',
        'Set realistic timelines for investigation completion'
      ]
    },
    {
      title: 'Running Fraud Detection',
      description: 'How to execute fraud detection analysis',
      steps: [
        'Access the Fraud Detection module',
        'Select data sources and time ranges',
        'Configure detection parameters and thresholds',
        'Run the analysis and review results',
        'Investigate flagged transactions'
      ],
      tips: [
        'Start with broader parameters and refine based on results',
        'Review false positives to improve detection accuracy',
        'Document all investigation findings and decisions'
      ]
    },
    {
      title: 'Performing Reconciliation',
      description: 'How to reconcile financial transactions',
      steps: [
        'Access the Reconciliation module',
        'Select accounts and date ranges',
        'Upload or connect data sources',
        'Configure matching rules and criteria',
        'Execute reconciliation and review results',
        'Resolve exceptions and discrepancies'
      ],
      tips: [
        'Establish clear reconciliation rules before starting',
        'Review exceptions systematically to identify patterns',
        'Maintain detailed audit trails for all adjustments'
      ]
    },
    {
      title: 'Generating Reports',
      description: 'How to create and customize reports',
      steps: [
        'Navigate to the Reporting module',
        'Select report template or create custom report',
        'Choose data sources and filters',
        'Configure report parameters and formatting',
        'Generate and preview the report',
        'Export or schedule report delivery'
      ],
      tips: [
        'Use templates for common report types',
        'Set up automated report scheduling for regular updates',
        'Include executive summaries for complex reports'
      ]
    }
  ];

  const bestPractices = [
    {
      title: 'Data Security',
      description: 'Maintaining data confidentiality and integrity',
      icon: '🔒',
      practices: [
        'Always log out when leaving your workstation',
        'Use strong, unique passwords for your account',
        'Never share your login credentials',
        'Report any suspicious activity immediately',
        'Follow data retention and disposal policies'
      ]
    },
    {
      title: 'Investigation Process',
      description: 'Following proper investigation procedures',
      icon: '📝',
      practices: [
        'Document every step of your investigation',
        'Maintain chain of custody for evidence',
        'Use consistent naming conventions',
        'Regularly update case status and notes',
        'Collaborate with team members effectively'
      ]
    },
    {
      title: 'Quality Assurance',
      description: 'Ensuring accuracy and reliability',
      icon: '✅',
      practices: [
        'Double-check all data entries and calculations',
        'Validate findings with multiple sources',
        'Peer review critical decisions and reports',
        'Maintain version control for documents',
        'Conduct regular quality audits'
      ]
    },
    {
      title: 'Communication',
      description: 'Effective communication with stakeholders',
      icon: '💬',
      practices: [
        'Provide regular status updates',
        'Use clear, professional language',
        'Escalate issues promptly when needed',
        'Maintain detailed communication logs',
        'Follow up on action items and commitments'
      ]
    }
  ];

  const troubleshooting = [
    {
      issue: 'Cannot access platform features',
      symptoms: ['Access denied errors', 'Feature buttons disabled', 'Permission errors'],
      solutions: [
        'Check your user role and permissions',
        'Contact your system administrator',
        'Verify your account is active',
        'Clear browser cache and cookies'
      ]
    },
    {
      issue: 'Slow system performance',
      symptoms: ['Long loading times', 'Unresponsive interface', 'Timeout errors'],
      solutions: [
        'Check your internet connection',
        'Close unnecessary browser tabs',
        'Clear browser cache and cookies',
        'Contact support if issue persists'
      ]
    },
    {
      issue: 'Data not loading',
      symptoms: ['Empty data tables', 'Loading spinners', 'Error messages'],
      solutions: [
        'Verify data source connections',
        'Check date range selections',
        'Refresh the page',
        'Contact technical support'
      ]
    },
    {
      issue: 'Report generation fails',
      symptoms: ['Error messages', 'Incomplete reports', 'Export failures'],
      solutions: [
        'Check data availability for selected parameters',
        'Verify export format compatibility',
        'Ensure sufficient storage space',
        'Try generating smaller reports'
      ]
    }
  ];

  return (
    <Layout>
      <div className="layout">
        <h1>Nexus Platform User Guide</h1>
        <p className="text-gray-600">
          Comprehensive guide to using the Nexus Platform for forensic analysis, fraud detection, and financial reconciliation.
        </p>

        {/* User Roles Section */}
        <section className="mt-8">
          <h2>User Roles and Responsibilities</h2>
          <p>Understanding your role helps you access the right features and perform your duties effectively.</p>
          
          <div className="roles-grid">
            {userRoles.map((role, index) => (
              <div key={index} className="role-card">
                <div className="role-icon">{role.icon}</div>
                <h3 className="role-title">{role.title}</h3>
                <p className="role-description">{role.description}</p>
                
                <h4>Key Responsibilities:</h4>
                <ul>
                  {role.responsibilities.map((resp, idx) => (
                    <li key={idx}>{resp}</li>
                  ))}
                </ul>
                
                <h4>Platform Access:</h4>
                <div className="access-tags">
                  {role.access.map((access, idx) => (
                    <span key={idx} className="access-tag">{access}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Platform Features Section */}
        <section className="mt-8">
          <h2>Platform Features Overview</h2>
          <p>Explore the key features available in the Nexus Platform.</p>
          
          <div className="features-grid">
            {platformFeatures.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
                
                <h4>Capabilities:</h4>
                <ul>
                  {feature.details.map((detail, idx) => (
                    <li key={idx}>{detail}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Common Tasks Section */}
        <section className="mt-8">
          <h2>Common Tasks and Workflows</h2>
          <p>Step-by-step guides for the most common platform activities.</p>
          
          <div className="steps-container">
            {commonTasks.map((task, index) => (
              <div key={index} className="step-card">
                <div className="step-header">
                  <div className="step-number">{index + 1}</div>
                  <div>
                    <h3 className="step-title">{task.title}</h3>
                    <p className="step-description">{task.description}</p>
                  </div>
                </div>
                
                <div className="step-details">
                  <h4>Steps:</h4>
                  <ol>
                    {task.steps.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ol>
                  
                  <h4>Pro Tips:</h4>
                  <ul>
                    {task.tips.map((tip, idx) => (
                      <li key={idx}>{tip}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Best Practices Section */}
        <section className="mt-8">
          <h2>Best Practices</h2>
          <p>Follow these guidelines to ensure effective and secure platform usage.</p>
          
          <div className="tips-grid">
            {bestPractices.map((practice, index) => (
              <div key={index} className="tip-card">
                <div className="tip-icon">{practice.icon}</div>
                <h4>{practice.title}</h4>
                <p>{practice.description}</p>
                
                <ul>
                  {practice.practices.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        {/* Troubleshooting Section */}
        <section className="mt-8">
          <h2>Troubleshooting Common Issues</h2>
          <p>Solutions for frequently encountered problems.</p>
          
          <div className="troubleshooting-list">
            {troubleshooting.map((item, index) => (
              <div key={index} className="troubleshooting-item">
                <h4>{item.issue}</h4>
                
                <h5>Symptoms:</h5>
                <ul>
                  {item.symptoms.map((symptom, idx) => (
                    <li key={idx}>{symptom}</li>
                  ))}
                </ul>
                
                <h5>Solutions:</h5>
                <ol>
                  {item.solutions.map((solution, idx) => (
                    <li key={idx}>{solution}</li>
                  ))}
                </ol>
              </div>
            ))}
          </div>
        </section>

        {/* Support and Resources Section */}
        <section className="mt-8">
          <h2>Support and Resources</h2>
          <p>Get help when you need it and access additional learning resources.</p>
          
          <div className="support-options">
            <Link href="/guide/quickstart" className="support-option">
              <span className="support-icon">🚀</span>
              <span>Quick Start Guide</span>
            </Link>
            
            <Link href="/dashboard" className="support-option">
              <span className="support-icon">📊</span>
              <span>System Dashboard</span>
            </Link>
            
            <a href="mailto:support@nexusplatform.com" className="support-option">
              <span className="support-icon">📧</span>
              <span>Email Support</span>
            </a>
            
            <a href="tel:+1-800-NEXUS-1" className="support-option">
              <span className="support-icon">📞</span>
              <span>Phone Support</span>
            </a>
          </div>
        </section>

        {/* Next Steps Section */}
        <section className="mt-8">
          <h2>Next Steps</h2>
          <p>Continue your learning journey with these recommended resources.</p>
          
          <div className="next-steps-grid">
            <div className="next-step">
              <h4>Complete the Quick Start Guide</h4>
              <p>Follow the step-by-step quick start guide to get familiar with the platform basics.</p>
              <Link href="/guide/quickstart" className="btn btn-primary">
                Start Quick Start Guide
              </Link>
            </div>
            
            <div className="next-step">
              <h4>Explore the Dashboard</h4>
              <p>Visit the system dashboard to see real-time platform status and metrics.</p>
              <Link href="/dashboard" className="btn btn-primary">
                Go to Dashboard
              </Link>
            </div>
            
            <div className="next-step">
              <h4>Practice with Sample Data</h4>
              <p>Use the sample datasets to practice platform features in a safe environment.</p>
              <Link href="/guide/sample-data" className="btn btn-primary">
                Access Sample Data
              </Link>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
