import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, Activity, FileText, CheckCircle2, XCircle, 
  Upload, Play, AlertCircle, RefreshCw, BarChart2, CheckSquare
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [health, setHealth] = useState({ status: 'loading', gemini_configured: false });
  const [grievances, setGrievances] = useState([]);
  const [alertError, setAlertError] = useState(null);

  // Extraction state
  const [extractText, setExtractText] = useState('');
  const [extractFile, setExtractFile] = useState(null);
  const [extracting, setExtracting] = useState(false);

  // Audit state
  const [auditGoal, setAuditGoal] = useState('Audit incoming grievances, calculate severity indices, and route critical infrastructure failures to municipal authorities.');
  const [currentSession, setCurrentSession] = useState(null);
  const [auditing, setAuditing] = useState(false);
  const [approvalReason, setApprovalReason] = useState('');

  // Initial load
  useEffect(() => {
    fetchHealth();
    loadSampleData();
  }, []);

  const fetchHealth = async () => {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      setHealth(data);
    } catch (err) {
      setHealth({ status: 'offline', gemini_configured: false });
    }
  };

  const loadSampleData = async () => {
    try {
      const res = await fetch('/api/sample');
      const data = await res.json();
      setGrievances(data);
      setAlertError(null);
    } catch (err) {
      setAlertError("Failed to connect to backend service.");
    }
  };

  const handleExtract = async () => {
    if (!extractText.trim() && !extractFile) {
      setAlertError("Provide text description or select a file.");
      return;
    }

    setExtracting(true);
    setAlertError(null);

    const formData = new FormData();
    if (extractText) formData.append('text', extractText);
    if (extractFile) formData.append('file', extractFile);

    try {
      const res = await fetch('/api/extract', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Extraction failed");
      }

      setGrievances(prev => [...data.grievances, ...prev]);
      setExtractText('');
      setExtractFile(null);
    } catch (err) {
      setAlertError(err.message);
    } finally {
      setExtracting(false);
    }
  };

  const handleRunAudit = async () => {
    if (grievances.length === 0) {
      setAlertError("Load grievances before running an audit.");
      return;
    }

    setAuditing(true);
    setAlertError(null);

    try {
      const res = await fetch('/api/audits', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grievances, goal: auditGoal })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Audit execution failed");

      setCurrentSession(data);
      setActiveTab('audit');
    } catch (err) {
      setAlertError(err.message);
    } finally {
      setAuditing(false);
    }
  };

  const handleApproval = async (decision) => {
    if (!currentSession) return;

    try {
      const res = await fetch(`/api/audits/${currentSession.session_id}/approval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, reason: approvalReason || null })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Approval action failed");

      setCurrentSession(data);
    } catch (err) {
      setAlertError(err.message);
    }
  };

  // Metrics computation
  const totalGrievances = grievances.length;
  const criticalCount = grievances.filter(g => g.severity === 'Critical').length;
  const highCount = grievances.filter(g => g.severity === 'High').length;
  const mediumCount = grievances.filter(g => g.severity === 'Medium').length;
  const lowCount = grievances.filter(g => g.severity === 'Low').length;

  const categoryCounts = grievances.reduce((acc, g) => {
    acc[g.category] = (acc[g.category] || 0) + 1;
    return acc;
  }, {});

  const severityChartData = [
    { name: 'Critical', count: criticalCount, fill: '#ef4444' },
    { name: 'High', count: highCount, fill: '#f97316' },
    { name: 'Medium', count: mediumCount, fill: '#f59e0b' },
    { name: 'Low', count: lowCount, fill: '#64748b' }
  ];

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="brand-icon">
            <Activity color="#ffffff" size={20} />
          </div>
          <div>
            <div className="brand-title">CURE</div>
            <div className="brand-caption">CIVIC REPAIR ENGINE</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <BarChart2 size={18} />
            Overview Dashboard
          </button>
          <button 
            className={`nav-item ${activeTab === 'grievances' ? 'active' : ''}`}
            onClick={() => setActiveTab('grievances')}
          >
            <FileText size={18} />
            Grievance Extraction
          </button>
          <button 
            className={`nav-item ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            <ShieldAlert size={18} />
            Agent Routing Audit
          </button>
        </nav>

        <div className="sidebar-footer">
          Demo-safe mode · Local simulation only
        </div>
      </aside>

      {/* Main Region */}
      <main className="main-content">
        {/* Top Header */}
        <header className="top-header">
          <h1 className="header-title">Civic Triage & Infrastructure Dashboard</h1>
          <div className="header-actions">
            <div className={`badge-status ${health.gemini_configured ? 'connected' : 'demo'}`}>
              <span className={`status-dot ${health.gemini_configured ? 'connected' : 'demo'}`}></span>
              {health.gemini_configured ? 'Gemini Connected' : 'Demo Mode Available'}
            </div>
            <button className="btn btn-secondary" onClick={loadSampleData}>
              <RefreshCw size={14} />
              Load Sample Data
            </button>
          </div>
        </header>

        <div className="content-body">
          {/* Dismissible Alert Banner */}
          {alertError && (
            <div className="alert-banner">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={16} />
                <span>{alertError}</span>
              </div>
              <button 
                onClick={() => setAlertError(null)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}
              >
                ×
              </button>
            </div>
          )}

          {/* Metric Summary Cards */}
          <section className="metrics-grid">
            <div className="metric-card">
              <span className="metric-label">Total Grievances</span>
              <span className="metric-value">{totalGrievances}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Critical Alerts</span>
              <span className="metric-value" style={{ color: '#ef4444' }}>{criticalCount}</span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Primary Department</span>
              <span className="metric-value" style={{ fontSize: '1.1rem' }}>
                Transportation
              </span>
            </div>
            <div className="metric-card">
              <span className="metric-label">Actionable Dispatches</span>
              <span className="metric-value" style={{ color: '#10b981' }}>
                {currentSession?.pending_action ? 1 : 0}
              </span>
            </div>
          </section>

          {/* TAB 1: OVERVIEW DASHBOARD */}
          {activeTab === 'overview' && (
            <>
              <section className="analytics-grid">
                <div className="panel-card">
                  <h2 className="panel-title">Severity Level Breakdown</h2>
                  <div style={{ width: '100%', height: 200 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={severityChartData}>
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count">
                          {severityChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="panel-card">
                  <h2 className="panel-title">Category Distribution</h2>
                  <div className="category-list">
                    {Object.entries(categoryCounts).map(([cat, count]) => {
                      const pct = totalGrievances > 0 ? (count / totalGrievances) * 100 : 0;
                      return (
                        <div key={cat} className="category-item">
                          <div className="category-header">
                            <span>{cat}</span>
                            <span>{count} ({pct.toFixed(0)}%)</span>
                          </div>
                          <div className="progress-bar-bg">
                            <div 
                              className="progress-bar-fill" 
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </section>

              {/* Data Table */}
              <section className="panel-card">
                <h2 className="panel-title">Active Civic Grievances</h2>
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>TITLE</th>
                        <th>DATE</th>
                        <th>CATEGORY</th>
                        <th>SEVERITY</th>
                        <th>LOCATION</th>
                      </tr>
                    </thead>
                    <tbody>
                      {grievances.map((g, idx) => (
                        <tr key={idx}>
                          <td style={{ fontWeight: 600 }}>{g.title}</td>
                          <td>{g.date || "Date unclear"}</td>
                          <td>{g.category}</td>
                          <td>
                            <span className={`severity-badge severity-${g.severity}`}>
                              {g.severity}
                            </span>
                          </td>
                          <td>{g.location || "Location unclear"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </>
          )}

          {/* TAB 2: EXTRACTION PANEL */}
          {activeTab === 'grievances' && (
            <section className="panel-card">
              <h2 className="panel-title">Multimodal GenAI Grievance Extraction</h2>
              <div className="extraction-panel">
                <textarea
                  className="text-area"
                  placeholder="Paste raw citizen report description (e.g., 2026-09-14 Severe water leak main street valve leaking heavily)..."
                  value={extractText}
                  onChange={(e) => setExtractText(e.target.value)}
                />

                <div className="dropzone">
                  <input
                    type="file"
                    id="file-upload"
                    style={{ display: 'none' }}
                    onChange={(e) => setExtractFile(e.target.files[0] || null)}
                  />
                  <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
                    <Upload size={24} style={{ marginBottom: '0.5rem', color: '#64748b' }} />
                    <div>
                      {extractFile ? extractFile.name : 'Upload file (PNG, JPG, MP3, WAV, CSV, TXT - Max 12 MB)'}
                    </div>
                  </label>
                  {extractFile && (
                    <button 
                      className="btn btn-secondary" 
                      style={{ marginTop: '0.5rem' }}
                      onClick={() => setExtractFile(null)}
                    >
                      Remove File
                    </button>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button className="btn btn-primary" onClick={handleExtract} disabled={extracting}>
                    {extracting ? 'Extracting...' : 'Extract Grievances'}
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => setExtractText('2026-09-16 Dangerous high-voltage electrical wire hanging above sidewalk at 5th Avenue intersection.')}
                  >
                    Use Example Text
                  </button>
                </div>
              </div>
            </section>
          )}

          {/* TAB 3: AGENT ROUTING AUDIT */}
          {activeTab === 'audit' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <section className="panel-card">
                <h2 className="panel-title">Agent Routing Goal & Execution</h2>
                <textarea
                  className="text-area"
                  style={{ height: '60px' }}
                  value={auditGoal}
                  onChange={(e) => setAuditGoal(e.target.value)}
                />
                <button className="btn btn-primary" onClick={handleRunAudit} disabled={auditing}>
                  <Play size={14} />
                  {auditing ? 'Running Bounded Audit...' : 'Run Agent Audit'}
                </button>
              </section>

              {currentSession && (
                <section className="panel-card">
                  <h2 className="panel-title">Audit Trace Log & Human Approval Gate</h2>
                  
                  {/* Summary Box */}
                  <div style={{ padding: '0.75rem', backgroundColor: '#e0f2fe', borderRadius: '6px', fontSize: '0.875rem' }}>
                    <strong>Session Status:</strong> {currentSession.status.toUpperCase()} | {currentSession.summary}
                  </div>

                  {/* Human Approval Gate Panel */}
                  {currentSession.pending_action && (
                    <div style={{ border: '1px solid #cbd5e1', borderRadius: '6px', padding: '1rem', backgroundColor: '#f8fafc' }}>
                      <h3 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', fontWeight: 600 }}>
                        Human-in-the-Loop Approval Required
                      </h3>
                      
                      <div className="dispatch-draft-box">
                        <span className="not-sent-badge">NOT SENT</span>
                        {currentSession.pending_action.notice_text}
                      </div>

                      {currentSession.status === 'awaiting_approval' ? (
                        <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                          <input
                            type="text"
                            placeholder="Optional approval/rejection rationale..."
                            className="text-area"
                            style={{ height: '40px' }}
                            value={approvalReason}
                            onChange={(e) => setApprovalReason(e.target.value)}
                          />
                          <div style={{ display: 'flex', gap: '1rem' }}>
                            <button className="btn btn-primary" onClick={() => handleApproval('approve')}>
                              <CheckCircle2 size={16} /> Approve (Simulation)
                            </button>
                            <button className="btn btn-danger" onClick={() => handleApproval('reject')}>
                              <XCircle size={16} /> Reject
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div style={{ marginTop: '0.75rem', fontWeight: 600, color: currentSession.pending_action.approved ? '#10b981' : '#ef4444' }}>
                          Action Decision Recorded: {currentSession.pending_action.approved ? 'APPROVED (Simulated)' : 'REJECTED'}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Audit Timeline */}
                  <div className="timeline">
                    {currentSession.audit_log.map((log, idx) => (
                      <div key={idx} className="timeline-item">
                        <div className="timeline-dot"></div>
                        <span className="timeline-time">{new Date(log.time).toLocaleTimeString()}</span>
                        <span className="timeline-msg">{log.message}</span>
                        {Object.keys(log.details || {}).length > 0 && (
                          <pre className="timeline-details">
                            {JSON.stringify(log.details, null, 2)}
                          </pre>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
