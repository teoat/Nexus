// NEXUS_app/frontend/pages/forensic-analysis.tsx
import Layout from '../../components/Layout';
import { useState, useEffect } from 'react';

export default function ForensicAnalysis() {
  const [selectedCase, setSelectedCase] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [aiInsights, setAiInsights] = useState([]);
  const [analysisProgress, setAnalysisProgress] = useState(0);

  const cases = [
    { id: 1, title: 'Case #2024-001', status: 'active', evidenceCount: 47 },
    { id: 2, title: 'Case #2024-002', status: 'pending', evidenceCount: 23 },
    { id: 3, title: 'Case #2024-003', status: 'completed', evidenceCount: 89 }
  ];

  const evidenceTypes = [
    { type: 'Document', count: 15, processed: 12 },
    { type: 'Image', count: 8, processed: 8 },
    { type: 'Video', count: 3, processed: 1 },
    { type: 'Audio', count: 2, processed: 2 },
    { type: 'Network Log', count: 19, processed: 19 }
  ];

  return (
    <Layout title="Forensic Analysis" userRole="investigator">
      <div className="forensic-analysis">
        {/* Case Selection */}
        <div className="case-selection">
          <h2>Select Case for Analysis</h2>
          <div className="cases-grid">
            {cases.map(case => (
              <div 
                key={case.id} 
                className={`case-card ${selectedCase?.id === case.id ? 'selected' : ''}`}
                onClick={() => setSelectedCase(case)}
              >
                <div className="case-header">
                  <h3>{case.title}</h3>
                  <span className={`case-status ${case.status}`}>{case.status}</span>
                </div>
                <div className="case-metrics">
                  <div className="metric">
                    <span className="metric-label">Evidence Items:</span>
                    <span className="metric-value">{case.evidenceCount}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {selectedCase && (
          <>
            {/* Evidence Upload */}
            <div className="evidence-upload">
              <h2>Evidence Management</h2>
              <div className="upload-area">
                <div className="upload-zone">
                  <div className="upload-icon">📁</div>
                  <h3>Drag & Drop Evidence Files</h3>
                  <p>or click to browse files</p>
                  <input type="file" multiple className="file-input" />
                </div>
              </div>
              
              <div className="evidence-types">
                <h3>Evidence by Type</h3>
                <div className="types-grid">
                  {evidenceTypes.map((type, index) => (
                    <div key={index} className="type-card">
                      <div className="type-header">
                        <h4>{type.type}</h4>
                        <span className="type-count">{type.count} items</span>
                      </div>
                      <div className="type-progress">
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{width: `${(type.processed / type.count) * 100}%`}}
                          ></div>
                        </div>
                        <span className="progress-text">{type.processed}/{type.count} processed</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Pattern Recognition */}
            <div className="ai-analysis">
              <h2>AI-Powered Pattern Recognition</h2>
              <div className="analysis-controls">
                <button className="btn btn-primary">Start Analysis</button>
                <button className="btn btn-secondary">Pause Analysis</button>
                <button className="btn btn-secondary">Export Results</button>
              </div>
              
              <div className="analysis-progress">
                <div className="progress-header">
                  <h3>Analysis Progress</h3>
                  <span className="progress-percentage">{analysisProgress}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{width: `${analysisProgress}%`}}
                  ></div>
                </div>
              </div>

              <div className="ai-insights">
                <h3>AI Insights</h3>
                <div className="insights-grid">
                  <div className="insight-card">
                    <div className="insight-icon">🔍</div>
                    <div className="insight-content">
                      <h4>Pattern Detected</h4>
                      <p>Unusual transaction pattern identified in financial records</p>
                      <div className="insight-confidence">
                        <span className="confidence-label">Confidence:</span>
                        <span className="confidence-value">87%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="insight-card">
                    <div className="insight-icon">⚠️</div>
                    <div className="insight-content">
                      <h4>Anomaly Found</h4>
                      <p>Suspicious file modification timestamps detected</p>
                      <div className="insight-confidence">
                        <span className="confidence-label">Confidence:</span>
                        <span className="confidence-value">92%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="insight-card">
                    <div className="insight-icon">🔗</div>
                    <div className="insight-content">
                      <h4>Connection Identified</h4>
                      <p>Link found between multiple evidence items</p>
                      <div className="insight-confidence">
                        <span className="confidence-label">Confidence:</span>
                        <span className="confidence-value">78%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Timeline Reconstruction */}
            <div className="timeline-reconstruction">
              <h2>Timeline Reconstruction</h2>
              <div className="timeline-container">
                <div className="timeline-item">
                  <div className="timeline-marker"></div>
                  <div className="timeline-content">
                    <div className="timeline-time">2024-01-15 14:30:22</div>
                    <div className="timeline-event">Document created: financial_report.pdf</div>
                    <div className="timeline-source">Evidence ID: E001</div>
                  </div>
                </div>
                
                <div className="timeline-item">
                  <div className="timeline-marker"></div>
                  <div className="timeline-content">
                    <div className="timeline-time">2024-01-15 15:45:18</div>
                    <div className="timeline-event">File modified: financial_report.pdf</div>
                    <div className="timeline-source">Evidence ID: E001</div>
                  </div>
                </div>
                
                <div className="timeline-item">
                  <div className="timeline-marker"></div>
                  <div className="timeline-content">
                    <div className="timeline-time">2024-01-15 16:12:45</div>
                    <div className="timeline-event">Email sent: suspicious_transaction@email.com</div>
                    <div className="timeline-source">Evidence ID: E002</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Network Analysis */}
            <div className="network-analysis">
              <h2>Network Analysis</h2>
              <div className="network-visualization">
                <div className="network-node central">
                  <div className="node-label">Main Server</div>
                </div>
                <div className="network-connections">
                  <div className="connection">
                    <div className="network-node">Client A</div>
                    <div className="connection-line"></div>
                  </div>
                  <div className="connection">
                    <div className="network-node">Client B</div>
                    <div className="connection-line"></div>
                  </div>
                  <div className="connection">
                    <div className="network-node">External IP</div>
                    <div className="connection-line suspicious"></div>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}