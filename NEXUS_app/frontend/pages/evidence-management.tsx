// NEXUS_app/frontend/pages/evidence-management.tsx
import Layout from '../../components/Layout';
import { useState, useEffect } from 'react';

export default function EvidenceManagement() {
  const [evidence, setEvidence] = useState([]);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  const evidenceTypes = ['Document', 'Image', 'Video', 'Audio', 'Network Log', 'Database', 'Email'];

  useEffect(() => {
    // Simulate evidence data
    const mockEvidence = [
      {
        id: 1,
        name: 'financial_report.pdf',
        type: 'Document',
        size: '2.3 MB',
        uploaded: '2024-01-15 14:30:22',
        status: 'processed',
        caseId: '2024-001',
        hash: 'a1b2c3d4e5f6...',
        chainOfCustody: [
          { user: 'John Doe', action: 'Uploaded', timestamp: '2024-01-15 14:30:22' },
          { user: 'Jane Smith', action: 'Reviewed', timestamp: '2024-01-15 15:45:18' }
        ]
      },
      {
        id: 2,
        name: 'screenshot_001.png',
        type: 'Image',
        size: '1.8 MB',
        uploaded: '2024-01-15 16:12:45',
        status: 'processing',
        caseId: '2024-001',
        hash: 'b2c3d4e5f6a1...',
        chainOfCustody: [
          { user: 'John Doe', action: 'Uploaded', timestamp: '2024-01-15 16:12:45' }
        ]
      }
    ];
    setEvidence(mockEvidence);
  }, []);

  return (
    <Layout title="Evidence Management" userRole="investigator">
      <div className="evidence-management">
        {/* Evidence Upload */}
        <div className="evidence-upload">
          <h2>Upload Evidence</h2>
          <div className="upload-section">
            <div className="upload-area">
              <div className="upload-zone">
                <div className="upload-icon">📁</div>
                <h3>Drag & Drop Evidence Files</h3>
                <p>Supports: PDF, DOC, XLS, JPG, PNG, MP4, MP3, TXT, LOG</p>
                <input type="file" multiple className="file-input" />
              </div>
            </div>
            
            <div className="upload-options">
              <div className="option-group">
                <label>Case ID</label>
                <select>
                  <option value="2024-001">Case #2024-001</option>
                  <option value="2024-002">Case #2024-002</option>
                  <option value="2024-003">Case #2024-003</option>
                </select>
              </div>
              
              <div className="option-group">
                <label>Evidence Type</label>
                <select>
                  {evidenceTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              
              <div className="option-group">
                <label>Priority</label>
                <select>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Evidence Search and Filter */}
        <div className="evidence-search">
          <h2>Evidence Library</h2>
          <div className="search-controls">
            <div className="search-input-group">
              <input 
                type="text" 
                placeholder="Search evidence..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              <button className="btn btn-primary">Search</button>
            </div>
            
            <div className="filter-controls">
              <select 
                value={filterType} 
                onChange={(e) => setFilterType(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Types</option>
                {evidenceTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              
              <select className="filter-select">
                <option value="all">All Cases</option>
                <option value="2024-001">Case #2024-001</option>
                <option value="2024-002">Case #2024-002</option>
              </select>
            </div>
          </div>
        </div>

        {/* Evidence List */}
        <div className="evidence-list">
          <div className="evidence-grid">
            {evidence.map(item => (
              <div 
                key={item.id} 
                className={`evidence-card ${selectedEvidence?.id === item.id ? 'selected' : ''}`}
                onClick={() => setSelectedEvidence(item)}
              >
                <div className="evidence-header">
                  <div className="evidence-icon">
                    {item.type === 'Document' ? '📄' : 
                     item.type === 'Image' ? '🖼️' : 
                     item.type === 'Video' ? '🎥' : 
                     item.type === 'Audio' ? '🎵' : '📋'}
                  </div>
                  <div className="evidence-status">
                    <span className={`status-badge ${item.status}`}>{item.status}</span>
                  </div>
                </div>
                
                <div className="evidence-content">
                  <h3 className="evidence-name">{item.name}</h3>
                  <div className="evidence-meta">
                    <div className="meta-item">
                      <span className="meta-label">Type:</span>
                      <span className="meta-value">{item.type}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Size:</span>
                      <span className="meta-value">{item.size}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Case:</span>
                      <span className="meta-value">{item.caseId}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">Uploaded:</span>
                      <span className="meta-value">{item.uploaded}</span>
                    </div>
                  </div>
                </div>
                
                <div className="evidence-actions">
                  <button className="btn btn-small">View</button>
                  <button className="btn btn-small">Download</button>
                  <button className="btn btn-small">Edit</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Evidence Detail Panel */}
        {selectedEvidence && (
          <div className="evidence-detail">
            <h2>Evidence Details</h2>
            <div className="detail-content">
              <div className="detail-section">
                <h3>File Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Name:</span>