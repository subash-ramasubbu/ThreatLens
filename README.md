# 🛡️ ThreatLens

> AI-powered Threat Intelligence Platform

ThreatLens is an open-source threat intelligence platform that aggregates data from multiple security feeds, correlates threats using MITRE ATT&CK framework, and uses AI to provide plain-English security analysis.

---

## 🚀 Live Demo
- **Frontend:** https://threat-lens-theta.vercel.app
- **Backend API:** https://threatlens-api-golw.onrender.com
- **API Docs:** https://threatlens-api-golw.onrender.com/docs
---

## ✨ Features

- **Real-time Threat Ingestion** — pulls from AbuseIPDB, AlienVault OTX, and NVD/CVE
- **Correlation Engine** — scores threats 0–100, auto-tags, deduplicates
- **MITRE ATT&CK Mapping** — maps every threat to ATT&CK technique IDs
- **AI Analyst** — explains any IP, domain, hash, or CVE in plain English
- **Live Dashboard** — real-time charts, alerts, and threat tables
- **REST API** — fully documented OpenAPI spec

---

## 🏗️ Architecture
External Feeds (AbuseIPDB, OTX, NVD)
↓
Ingestion Layer (Python + httpx)
↓
Normalization → PostgreSQL + Redis
↓
Correlation Engine (scoring + MITRE ATT&CK)
↓
AI Analyst Layer (Groq LLaMA)
↓
REST API (FastAPI) → React Dashboard

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL, Redis |
| AI | Groq LLaMA 3.3 |
| Frontend | React, Recharts |
| Infrastructure | Docker, Docker Compose |

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11+
- Docker Desktop
- Node.js 18+

### Backend
```bash
git clone https://github.com/subash-ramasubbu/ThreatLens.git
cd ThreatLens
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
docker-compose up -d
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create a `.env` file:
DATABASE_URL=postgresql://postgres:password@localhost:5432/threatlens
REDIS_URL=redis://localhost:6379
ABUSEIPDB_API_KEY=<get from abuseipdb.com/account/api>
ALIENVAULT_API_KEY=<get from otx.alienvault.com/settings>
GROQ_API_KEY=<get from console.groq.com/keys>

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/threats` | Get all threats |
| POST | `/api/threats` | Add a threat |
| GET | `/api/threats/search?q=` | Search threats |
| POST | `/api/ingest/all` | Ingest from all sources |
| POST | `/api/correlate/run` | Run correlation engine |
| GET | `/api/correlate/alerts` | Get all alerts |
| GET | `/api/ai/analyze/{id}` | AI analysis by ID |
| POST | `/api/ai/analyze` | AI analysis for any indicator |
| GET | `/api/ai/report` | Generate threat report |

---

## 🔒 Security Standards

- MITRE ATT&CK Framework
- CVSS Scoring
- STIX2 compatible data model

---

## 👨‍💻 Author

**Subash Ramasubbu**
[GitHub](https://github.com/subash-ramasubbu) · [LinkedIn](www.linkedin.com/in/subash-r-)