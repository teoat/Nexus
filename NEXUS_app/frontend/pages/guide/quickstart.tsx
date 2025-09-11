import Layout from '../../components/Layout';
import Link from 'next/link';

export default function Quickstart() {
  const steps = [
    {
      number: 1,
      title: 'Platform Access',
      description: 'Access the Nexus Platform through your web browser',
      details: [
        'Navigate to the platform URL provided by your administrator',
        'Enter your credentials (username and password)',
        'Complete any required multi-factor authentication',
        'Review and accept the terms of service'
      ],
      icon: '🌐',
      link: '/guide/access-setup'
    },
    {
      number: 2,
      title: 'Role Selection',
      description: 'Choose your user role to access appropriate features',
      details: [
        'Select from Investigator, Compliance Officer, or Executive roles',
        'Review role-specific capabilities and permissions',
        'Confirm your role selection',
        'Access your personalized dashboard'
      ],
      icon: '👤',
      link: '/guide/role-selection'
    },
    {
      number: 3,
      title: 'Workspace Setup',
      description: 'Configure your personal workspace and preferences',
      details: [
        'Set up your profile information',
        'Configure notification preferences',
        'Choose your default dashboard layout',
        'Set up any required integrations'
      ],
      icon: '⚙️',
      link: '/guide/workspace-setup'
    },
    {
      number: 4,
      title: 'First Task',
      description: 'Complete your first guided task to learn the platform',
      details: [
        'Choose from available tutorial tasks',
        'Follow the step-by-step guidance',
        'Learn platform navigation and features',
        'Complete the task and review results'
      ],
      icon: '🎯',
      link: '/guide/first-task'
    },
    {
      number: 5,
      title: 'Advanced Features',
      description: 'Explore advanced platform capabilities',
      details: [
        'Learn about AI-powered analysis tools',
        'Understand fraud detection workflows',
        'Explore reconciliation processes',
        'Master evidence management'
      ],
      icon: '🚀',
      link: '/guide/advanced-features'
    }
  ];

  const roleCapabilities = [
    {
      role: 'Investigator',
      capabilities: [
        'Case Management',
        'Evidence Analysis',
        'Forensic Tools',
        'Report Generation',
        'Collaboration Tools'
      ],
      icon: '🔍'
    },
    {
      role: 'Compliance Officer',
      capabilities: [
        'Risk Assessment',
        'Compliance Monitoring',
        'Audit Trails',
        'Regulatory Reports',
        'Policy Management'
      ],
      icon: '📋'
    },
    {
      role: 'Executive',
      capabilities: [
        'Executive Dashboard',
        'Risk Overview',
        'Performance Metrics',
        'Strategic Insights',
        'High-level Reports'
      ],
      icon: '📊'
    }
  ];

  const commonTasks = [
    {
      title: 'Start a New Case',
      description: 'Create and manage forensic investigation cases',
      icon: '📁',
      link: '/guide/case-management'
    },
    {
      title: 'Upload Evidence',
      description: 'Securely upload and organize case evidence',
      icon: '📤',
      link: '/guide/evidence-upload'
    },
    {
      title: 'Run Fraud Analysis',
      description: 'Execute AI-powered fraud detection algorithms',
      icon: '🛡️',
      link: '/guide/fraud-analysis'
    },
    {
      title: 'Generate Reports',
      description: 'Create comprehensive case and compliance reports',
      icon: '📊',
      link: '/guide/report-generation'
    },
    {
      title: 'Collaborate with Team',
      description: 'Work together with team members on cases',
      icon: '👥',
      link: '/guide/collaboration'
    },
    {
      title: 'Monitor System Status',
      description: 'Track platform performance and health',
      icon: '📈',
      link: '/dashboard'
    }
  ];

  return (
    <Layout>
      <div className="quickstart-header">
        <h1>🚀 Nexus Platform Quickstart Guide</h1>
        <p className="quickstart-subtitle">
          Get up and running with the Nexus Platform in 5 simple steps
        </p>
      </div>

      <div className="quickstart-progress">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: '20%' }}></div>
        </div>
        <p className="progress-text">Step 1 of 5: Platform Access</p>
      </div>

      <div className="quickstart-content">
        <div className="steps-section">
          <h2>Getting Started Steps</h2>
          <div className="steps-container">
            {steps.map((step, index) => (
              <div key={index} className="step-card">
                <div className="step-header">
                  <div className="step-number">{step.number}</div>
                  <div className="step-icon">{step.icon}</div>
                  <h3 className="step-title">{step.title}</h3>
                </div>
                <p className="step-description">{step.description}</p>
                <div className="step-details">
                  <h4>What you'll do:</h4>
                  <ul>
                    {step.details.map((detail, dIndex) => (
                      <li key={dIndex}>{detail}</li>
                    ))}
                  </ul>
                </div>
                <div className="step-actions">
                  <Link href={step.link} className="btn btn-primary">
                    Start Step {step.number}
                  </Link>
                  {index < steps.length - 1 && (
                    <Link href={steps[index + 1].link} className="btn btn-secondary">
                      Next: {steps[index + 1].title}
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="roles-section">
          <h2>Understanding Your Role</h2>
          <p>
            The Nexus Platform provides different interfaces and capabilities based on your role. 
            Understanding your role will help you navigate the platform effectively.
          </p>
          <div className="roles-grid">
            {roleCapabilities.map((role, index) => (
              <div key={index} className="role-capability-card">
                <div className="role-header">
                  <div className="role-icon">{role.icon}</div>
                  <h3 className="role-title">{role.role}</h3>
                </div>
                <div className="role-capabilities">
                  <h4>Key Capabilities:</h4>
                  <ul>
                    {role.capabilities.map((capability, cIndex) => (
                      <li key={cIndex}>{capability}</li>
                    ))}
                  </ul>
                </div>
                <Link href={`/guide/${role.role.toLowerCase()}`} className="role-link">
                  Learn More About {role.role} Role →
                </Link>
              </div>
            ))}
          </div>
        </div>

        <div className="common-tasks-section">
          <h2>Common Tasks You'll Perform</h2>
          <p>
            Once you're familiar with the platform, here are some common tasks you'll perform regularly:
          </p>
          <div className="tasks-grid">
            {commonTasks.map((task, index) => (
              <Link key={index} href={task.link} className="task-card">
                <div className="task-icon">{task.icon}</div>
                <h4 className="task-title">{task.title}</h4>
                <p className="task-description">{task.description}</p>
                <div className="task-arrow">→</div>
              </Link>
            ))}
          </div>
        </div>

        <div className="tips-section">
          <h2>Pro Tips for Success</h2>
          <div className="tips-grid">
            <div className="tip-card">
              <div className="tip-icon">💡</div>
              <h4>Start Small</h4>
              <p>Begin with simple tasks to build confidence before tackling complex cases.</p>
            </div>
            <div className="tip-card">
              <div className="tip-icon">🔍</div>
              <h4>Use Search</h4>
              <p>The platform has comprehensive search functionality - use it to find what you need quickly.</p>
            </div>
            <div className="tip-card">
              <div className="tip-icon">📚</div>
              <h4>Read Documentation</h4>
              <p>Take time to read the detailed guides for each feature you plan to use.</p>
            </div>
            <div className="tip-card">
              <div className="tip-icon">👥</div>
              <h4>Collaborate</h4>
              <p>Don't hesitate to reach out to team members for help and collaboration.</p>
            </div>
          </div>
        </div>

        <div className="next-steps-section">
          <h2>What's Next?</h2>
          <p>
            After completing this quickstart guide, you'll be ready to:
          </p>
          <div className="next-steps-grid">
            <div className="next-step">
              <h4>🎯 Begin Your First Real Case</h4>
              <p>Apply what you've learned to actual forensic investigations</p>
              <Link href="/guide/first-case" className="btn btn-small">
                Start First Case
              </Link>
            </div>
            <div className="next-step">
              <h4>📊 Explore Advanced Analytics</h4>
              <p>Dive deeper into AI-powered analysis and reporting</p>
              <Link href="/guide/advanced-analytics" className="btn btn-small">
                Learn Analytics
              </Link>
            </div>
            <div className="next-step">
              <h4>⚙️ Customize Your Workspace</h4>
              <p>Personalize the platform to match your workflow</p>
              <Link href="/guide/customization" className="btn btn-small">
                Customize
              </Link>
            </div>
          </div>
        </div>

        <div className="support-section">
          <h2>Need Help?</h2>
          <p>
            If you encounter any issues or have questions during your setup:
          </p>
          <div className="support-options">
            <Link href="/guide/faq" className="support-option">
              <span className="support-icon">❓</span>
              <span>Check FAQ</span>
            </Link>
            <Link href="/guide/tutorials" className="support-option">
              <span className="support-icon">📚</span>
              <span>Video Tutorials</span>
            </Link>
            <Link href="/guide/support" className="support-option">
              <span className="support-icon">🆘</span>
              <span>Contact Support</span>
            </Link>
            <Link href="/guide/community" className="support-option">
              <span className="support-icon">👥</span>
              <span>Community Forum</span>
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}
