import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Shield, AlertTriangle, Brain, Search } from 'lucide-react';
import { api } from './api';
import './App.css';

const BASE_URL = 'https://threatlens-api-golw.onrender.com';

// eslint-disable-next-line no-unused-vars
const SEVERITY_COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
};

function Dashboard({ threats, alerts, onIngest, onCorrelate, loading }) {
  const critical = threats.filter(t => t.risk_score >= 85).length;
  const high = threats.filter(t => t.risk_score >= 65 && t.risk_score < 85).length;
  const medium = threats.filter(t => t.risk_score >= 40 && t.risk_score < 65).length;

  const pieData = [
    { name: 'Critical', value: critical, color: '#ef4444' },
    { name: 'High', value: high, color: '#f97316' },
    { name: 'Medium', value: medium, color: '#eab308' },
  ].filter(d => d.value > 0);

  const sourceData = threats.reduce((acc, t) => {
    acc[t.source] = (acc[t.source] || 0) + 1;
    return acc;
  }, {});

  const barData = Object.entries(sourceData).map(([source, count]) => ({
    source: source.toUpperCase(),
    count,
  }));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 className="page-title" style={{ margin: 0 }}>Dashboard</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-success" onClick={onIngest} disabled={loading}>
            {loading ? 'Loading...' : '⬇ Ingest Threats'}
          </button>
          <button className="btn btn-primary" onClick={onCorrelate} disabled={loading}>
            🔗 Run Correlation
          </button>
          <button
            className="btn"
            style={{ background: '#7c3aed', color: 'white' }}
            onClick={() => window.open(`${BASE_URL}/api/export/pdf`, '_blank')}
          >
            📄 Export PDF
          </button>
          <button
            className="btn"
            style={{ background: '#0f766e', color: 'white' }}
            onClick={() => window.open(`${BASE_URL}/api/export/stix2`, '_blank')}
          >
            📦 Export STIX2
          </button>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Threats</div>
          <div className="stat-value total">{threats.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Critical</div>
          <div className="stat-value critical">{critical}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">High</div>
          <div className="stat-value high">{high}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Alerts</div>
          <div className="stat-value medium">{alerts.length}</div>
        </div>
      </div>

      <div className="chart-grid">
        <div className="chart-card">
          <div className="chart-title">Threats by Source</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData}>
              <XAxis dataKey="source" tick={{ fill: '#64748b', fontSize: 11 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: '8px' }} />
              <Bar dataKey="count" fill="#38bdf8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-title">Severity Distribution</div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#0f1629', border: '1px solid #1e2d4a' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="table-card" style={{ marginBottom: '24px' }}>
        <div className="table-header">
          <span>Platform Statistics</span>
        </div>
        <div style={{ padding: '20px', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <div>
            <div className="stat-label">Total Monitored</div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#38bdf8' }}>{threats.length}</div>
          </div>
          <div>
            <div className="stat-label">Sources Active</div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#22c55e' }}>3</div>
          </div>
          <div>
            <div className="stat-label">AI Analyses</div>
            <div style={{ fontSize: '24px', fontWeight: '700', color: '#a855f7' }}>∞</div>
          </div>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header">
          <span>Recent Alerts</span>
          <span style={{ fontSize: '13px', color: '#64748b' }}>{alerts.length} total</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Level</th>
              <th>Type</th>
              <th>Value</th>
              <th>Risk Score</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {alerts.slice(0, 10).map((alert, i) => (
              <tr key={i}>
                <td><span className={`badge badge-${alert.level.toLowerCase()}`}>{alert.level}</span></td>
                <td>{alert.type.toUpperCase()}</td>
                <td style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{alert.value}</td>
                <td><span className="risk-score">{alert.risk_score}</span></td>
                <td>{alert.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ThreatsPage({ threats }) {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('risk_score');
  const [filtered, setFiltered] = useState(threats);

  useEffect(() => {
    let result = [...threats];
    if (search) {
      result = result.filter(t =>
        t.value.toLowerCase().includes(search.toLowerCase()) ||
        t.tags?.toLowerCase().includes(search.toLowerCase()) ||
        t.type.toLowerCase().includes(search.toLowerCase())
      );
    }
    if (typeFilter !== 'all') {
      result = result.filter(t => t.type === typeFilter);
    }
    result.sort((a, b) => {
      if (sortBy === 'risk_score') return b.risk_score - a.risk_score;
      if (sortBy === 'confidence') return b.confidence - a.confidence;
      return 0;
    });
    setFiltered(result);
  }, [search, typeFilter, sortBy, threats]);

  const types = ['all', ...new Set(threats.map(t => t.type))];

  return (
    <div>
      <h1 className="page-title">Threat Indicators</h1>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
        <input
          className="search-bar"
          style={{ margin: 0, flex: 1 }}
          placeholder="Search by value, tag, type..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          style={{ padding: '10px', background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: '8px', color: '#e2e8f0' }}
        >
          {types.map(t => (
            <option key={t} value={t}>{t.toUpperCase()}</option>
          ))}
        </select>
        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value)}
          style={{ padding: '10px', background: '#0f1629', border: '1px solid #1e2d4a', borderRadius: '8px', color: '#e2e8f0' }}
        >
          <option value="risk_score">Sort by Risk Score</option>
          <option value="confidence">Sort by Confidence</option>
        </select>
      </div>
      <div className="table-card">
        <div className="table-header">
          <span>Threat Indicators</span>
          <span style={{ fontSize: '13px', color: '#64748b' }}>{filtered.length} results</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Type</th>
              <th>Value</th>
              <th>Severity</th>
              <th>Risk Score</th>
              <th>Source</th>
              <th>Country</th>
              <th>Tags</th>
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 50).map(t => (
              <tr key={t.id}>
                <td style={{ color: '#64748b' }}>{t.id}</td>
                <td>{t.type.toUpperCase()}</td>
                <td style={{ fontFamily: 'monospace', color: '#38bdf8', fontSize: '12px' }}>{t.value}</td>
                <td><span className={`badge badge-${t.severity}`}>{t.severity}</span></td>
                <td><span className="risk-score">{t.risk_score}</span></td>
                <td>{t.source}</td>
                <td>{t.country || '—'}</td>
                <td><span className="tags">{t.tags}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AIPage() {
  const [indicator, setIndicator] = useState('');
  const [type, setType] = useState('ip');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const getVerdictStyle = (score) => {
    if (score >= 85) return {
      bg: 'linear-gradient(135deg, #450a0a 0%, #1a0505 100%)',
      border: '#ef4444',
      color: '#ef4444',
      label: '⚠ CRITICAL THREAT',
    };
    if (score >= 65) return {
      bg: 'linear-gradient(135deg, #431407 0%, #1a0a02 100%)',
      border: '#f97316',
      color: '#f97316',
      label: '🔶 HIGH THREAT',
    };
    if (score >= 40) return {
      bg: 'linear-gradient(135deg, #422006 0%, #1a1002 100%)',
      border: '#eab308',
      color: '#eab308',
      label: '⚡ MEDIUM THREAT',
    };
    return {
      bg: 'linear-gradient(135deg, #052e16 0%, #021a0a 100%)',
      border: '#22c55e',
      color: '#22c55e',
      label: '✅ SAFE',
    };
  };

  const extractMitre = (text) => {
    if (!text) return [];
    const matches = text.match(/T\d{4}(?:\.\d{3})?[^)"]*/g) || [];
    return [...new Set(matches)].slice(0, 4);
  };

  const extractSummary = (analysis) => {
    const s = analysis?.summary || analysis?.threat_assessment || '';
    const sentences = s.match(/[^.!?]+[.!?]+/g) || [];
    return sentences.slice(0, 2).join(' ').replace(/\*\*/g, '').trim();
  };

  const extractAction = (analysis) => {
    const s = analysis?.recommended_actions || '';
    const sentences = s.match(/[^.!?]+[.!?]+/g) || [];
    return sentences.slice(0, 2).join(' ').replace(/\*\*/g, '').replace(/\*/g, '').trim();
  };

  const analyze = async () => {
    if (!indicator) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await api.analyzeIndicator(indicator, type);
      setResult(res.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const score = result?.risk_score || 0;
  const verdict = getVerdictStyle(score);
  const mitreTechniques = extractMitre(result?.analysis?.attack_techniques || '');
  const summary = extractSummary(result?.analysis || {});
  const action = extractAction(result?.analysis || {});

  return (
    <div>
      <h1 className="page-title">AI Analyst</h1>

      <div className="analysis-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <select
            value={type}
            onChange={e => setType(e.target.value)}
            style={{ padding: '10px', background: '#0a0e1a', border: '1px solid #1e2d4a', borderRadius: '8px', color: '#e2e8f0', fontSize: '13px' }}
          >
            <option value="ip">IP Address</option>
            <option value="domain">Domain</option>
            <option value="hash">File Hash</option>
            <option value="cve">CVE</option>
          </select>
          <input
            className="search-bar"
            style={{ margin: 0, flex: 1 }}
            placeholder="Enter IP, domain, hash or CVE..."
            value={indicator}
            onChange={e => setIndicator(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && analyze()}
          />
          <button className="btn btn-primary" onClick={analyze} disabled={loading}>
            {loading ? 'Analyzing...' : '🔍 Analyze'}
          </button>
        </div>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
          <div style={{ fontSize: '32px', marginBottom: '12px' }}>🔍</div>
          <div>Analyzing threat intelligence...</div>
        </div>
      )}

      {result && !loading && (
        <div style={{
          background: verdict.bg,
          border: `1px solid ${verdict.border}`,
          borderRadius: '16px',
          padding: '24px',
        }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <div style={{ fontSize: '11px', color: verdict.color, fontWeight: '700', letterSpacing: '2px', marginBottom: '4px' }}>
                {verdict.label}
              </div>
              <div style={{ fontSize: '20px', fontWeight: '700', color: '#ffffff', fontFamily: 'monospace' }}>
                {result.indicator || indicator}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '42px', fontWeight: '900', color: verdict.color, lineHeight: 1 }}>{score}</div>
              <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>Risk Score</div>
            </div>
          </div>

          {/* What is it */}
          {summary && (
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '10px', padding: '14px', marginBottom: '12px' }}>
              <div style={{ fontSize: '11px', color: verdict.color, fontWeight: '700', letterSpacing: '1px', marginBottom: '6px' }}>WHAT IS IT</div>
              <div style={{ fontSize: '14px', color: '#f1f5f9', lineHeight: '1.6' }}>{summary}</div>
            </div>
          )}

          {/* Quick facts */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '12px' }}>
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '4px' }}>TYPE</div>
              <div style={{ fontSize: '14px', fontWeight: '700', color: '#ffffff' }}>{type.toUpperCase()}</div>
            </div>
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '4px' }}>CONFIDENCE</div>
              <div style={{ fontSize: '14px', fontWeight: '700', color: '#ffffff' }}>{result.analysis?.confidence_level?.split(' ')[0] || '—'}</div>
            </div>
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
              <div style={{ fontSize: '11px', color: '#64748b', marginBottom: '4px' }}>VERDICT</div>
              <div style={{ fontSize: '14px', fontWeight: '700', color: verdict.color }}>
                {score >= 85 ? 'BLOCK' : score >= 65 ? 'MONITOR' : score >= 40 ? 'REVIEW' : 'SAFE'}
              </div>
            </div>
          </div>

          {/* MITRE tags */}
          {mitreTechniques.length > 0 && (
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: '10px', padding: '14px', marginBottom: '12px' }}>
              <div style={{ fontSize: '11px', color: verdict.color, fontWeight: '700', letterSpacing: '1px', marginBottom: '8px' }}>MITRE ATT&CK</div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {mitreTechniques.map((t, i) => (
                  <span key={i} style={{ background: '#1e1a2e', border: '1px solid #6366f1', color: '#a5b4fc', padding: '4px 10px', borderRadius: '20px', fontSize: '12px', fontWeight: '600' }}>
                    {t.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Immediate action */}
          {action && (
            <div style={{ background: `rgba(${score >= 85 ? '239,68,68' : score >= 65 ? '249,115,22' : score >= 40 ? '234,179,8' : '34,197,94'},0.15)`, border: `1px solid rgba(${score >= 85 ? '239,68,68' : score >= 65 ? '249,115,22' : score >= 40 ? '234,179,8' : '34,197,94'},0.3)`, borderRadius: '10px', padding: '14px' }}>
              <div style={{ fontSize: '11px', color: verdict.color, fontWeight: '700', letterSpacing: '1px', marginBottom: '6px' }}>⚡ IMMEDIATE ACTION</div>
              <div style={{ fontSize: '14px', color: '#f1f5f9', lineHeight: '1.6' }}>{action}</div>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div style={{ display: 'flex', gap: '10px', marginTop: '24px' }}>
        {[
          { label: 'CRITICAL', bg: '#450a0a', border: '#ef4444', color: '#ef4444' },
          { label: 'HIGH', bg: '#431407', border: '#f97316', color: '#f97316' },
          { label: 'MEDIUM', bg: '#422006', border: '#eab308', color: '#eab308' },
          { label: 'SAFE', bg: '#052e16', border: '#22c55e', color: '#22c55e' },
        ].map((v, i) => (
          <div key={i} style={{ flex: 1, background: v.bg, border: `1px solid ${v.border}`, borderRadius: '8px', padding: '10px', textAlign: 'center', fontSize: '11px', color: v.color, fontWeight: '700' }}>
            {v.label}
          </div>
        ))}
      </div>
    </div>
  );
}

function HuntingPage() {
  const [query, setQuery] = useState('');
  const [huntType, setHuntType] = useState('tag');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const hunt = async () => {
    if (!query && huntType !== 'high-risk' && huntType !== 'c2') return;
    setLoading(true);
    try {
      let res;
      if (huntType === 'tag') res = await api.huntByTag(query);
      else if (huntType === 'mitre') res = await api.huntMitre(query);
      else if (huntType === 'high-risk') res = await api.huntHighRisk();
      else if (huntType === 'c2') res = await api.huntC2();
      setResults(res.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div>
      <h1 className="page-title">Threat Hunting</h1>
      <div className="analysis-card">
        <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
          <select
            value={huntType}
            onChange={e => setHuntType(e.target.value)}
            style={{ padding: '10px', background: '#0a0e1a', border: '1px solid #1e2d4a', borderRadius: '8px', color: '#e2e8f0' }}
          >
            <option value="tag">Hunt by Tag</option>
            <option value="mitre">Hunt by MITRE ATT&CK</option>
            <option value="high-risk">High Risk IPs</option>
            <option value="c2">C2 Infrastructure</option>
          </select>
          {(huntType === 'tag' || huntType === 'mitre') && (
            <input
              className="search-bar"
              style={{ margin: 0, flex: 1 }}
              placeholder={huntType === 'tag' ? 'Enter tag (e.g. ransomware)' : 'Enter technique (e.g. T1046)'}
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          )}
          <button className="btn btn-primary" onClick={hunt} disabled={loading}>
            {loading ? 'Hunting...' : '🔍 Hunt'}
          </button>
        </div>
      </div>
      {results && (
        <div className="table-card">
          <div className="table-header">
            <span>Hunt Results: {results.hunt_query}</span>
            <span style={{ fontSize: '13px', color: '#64748b' }}>{results.results} found</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Value</th>
                <th>Type</th>
                <th>Risk Score</th>
                <th>Tags</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {results.threats?.map((t, i) => (
                <tr key={i}>
                  <td style={{ fontFamily: 'monospace', color: '#38bdf8', fontSize: '12px' }}>{t.value}</td>
                  <td>{t.type?.toUpperCase()}</td>
                  <td><span className="risk-score">{t.risk_score}</span></td>
                  <td><span className="tags">{t.tags}</span></td>
                  <td>{t.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function MLPage() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const runML = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${BASE_URL}/api/ml/anomalies`);
      setResults(res.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div>
      <h1 className="page-title">ML Anomaly Detection</h1>
      <div className="analysis-card" style={{ marginBottom: '24px' }}>
        <p style={{ color: '#94a3b8', marginBottom: '16px' }}>
          Uses Isolation Forest algorithm to detect unusual threat patterns that don't match normal behavior.
        </p>
        <button className="btn btn-primary" onClick={runML} disabled={loading}>
          {loading ? 'Analyzing...' : '🤖 Run ML Detection'}
        </button>
      </div>
      {results && (
        <>
          <div className="stats-grid" style={{ marginBottom: '24px' }}>
            <div className="stat-card">
              <div className="stat-label">Total Analyzed</div>
              <div className="stat-value total">{results.total_analyzed}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Anomalies Found</div>
              <div className="stat-value critical">{results.anomalies_detected}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Anomaly Rate</div>
              <div className="stat-value high">{results.anomaly_rate}%</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Normal</div>
              <div className="stat-value medium">{results.normal_count}</div>
            </div>
          </div>
          <div className="table-card">
            <div className="table-header">
              <span>Top Anomalies</span>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Value</th>
                  <th>Type</th>
                  <th>Risk Score</th>
                  <th>Anomaly Score</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {results.top_anomalies?.map((a, i) => (
                  <tr key={i}>
                    <td style={{ fontFamily: 'monospace', color: '#38bdf8', fontSize: '12px' }}>{a.value}</td>
                    <td>{a.type?.toUpperCase()}</td>
                    <td><span className="risk-score">{a.risk_score}</span></td>
                    <td style={{ color: '#ef4444' }}>{a.anomaly_score}</td>
                    <td>{a.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [threats, setThreats] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    try {
      const [threatsRes, alertsRes] = await Promise.all([
        api.getAllThreats(),
        api.getAlerts(),
      ]);
      setThreats(threatsRes.data);
      setAlerts(alertsRes.data.alerts || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { loadData(); }, []);

  const handleIngest = async () => {
    setLoading(true);
    await api.ingestAll();
    await loadData();
    setLoading(false);
  };

  const handleCorrelate = async () => {
    setLoading(true);
    await api.runCorrelation();
    await loadData();
    setLoading(false);
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Shield },
    { id: 'threats', label: 'Threats', icon: AlertTriangle },
    { id: 'hunting', label: 'Threat Hunting', icon: Search },
    { id: 'ml', label: 'ML Detection', icon: Brain },
    { id: 'ai', label: 'AI Analyst', icon: Brain },
  ];

  return (
    <div className="app">
      <div className="sidebar">
        <div className="sidebar-logo">
          Threat<span className="logo-lens">Lens</span>
          <span className="logo-dot"></span>
        </div>
        {navItems.map(item => (
          <div
            key={item.id}
            className={`nav-item ${page === item.id ? 'active' : ''}`}
            onClick={() => setPage(item.id)}
          >
            <item.icon size={16} />
            {item.label}
          </div>
        ))}
      </div>

      <div className="main">
        {page === 'dashboard' && (
          <Dashboard
            threats={threats}
            alerts={alerts}
            onIngest={handleIngest}
            onCorrelate={handleCorrelate}
            loading={loading}
          />
        )}
        {page === 'threats' && <ThreatsPage threats={threats} />}
        {page === 'hunting' && <HuntingPage />}
        {page === 'ml' && <MLPage />}
        {page === 'ai' && <AIPage />}
      </div>
    </div>
  );
}