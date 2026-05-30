import axios from 'axios';

const BASE_URL = 'https://threatlens-api-golw.onrender.com';

export const api = {
  // Threats
  getAllThreats: (severity = null) => {
    const params = severity ? { severity } : {};
    return axios.get(`${BASE_URL}/api/threats/`, { params });
  },

  searchThreats: (query) =>
    axios.get(`${BASE_URL}/api/threats/search`, { params: { q: query } }),

  // Ingestion
  ingestAll: () =>
    axios.post(`${BASE_URL}/api/ingest/all`),

  // Correlation
  runCorrelation: () =>
    axios.post(`${BASE_URL}/api/correlate/run`),

  getAlerts: () =>
    axios.get(`${BASE_URL}/api/correlate/alerts`),

  // AI
  analyzeThreat: (id) =>
    axios.get(`${BASE_URL}/api/ai/analyze/${id}`),

  analyzeIndicator: (indicator, type) =>
    axios.post(`${BASE_URL}/api/ai/analyze`, { indicator, type }),

  getReport: () =>
    axios.get(`${BASE_URL}/api/ai/report`),
};