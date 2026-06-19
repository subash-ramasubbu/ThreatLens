# 🛡️ ThreatLens

> AI-powered Threat Intelligence Platform

ThreatLens is a production-grade, open-source threat intelligence platform that aggregates data from multiple security feeds, correlates threats using the MITRE ATT&CK framework, and uses AI to provide plain-English security analysis.

---

## 🚀 Live Demo
- **Frontend:** https://threat-lens-theta.vercel.app
- **Backend API:** https://threatlens-api-golw.onrender.com
- **API Docs:** https://threatlens-api-golw.onrender.com/docs

---

## ✨ Features

### Core Platform
- **Real-time Threat Ingestion** — pulls from AbuseIPDB, AlienVault OTX, and NVD/CVE
- **Correlation Engine** — scores threats 0–100, auto-tags, deduplicates
- **MITRE ATT&CK Mapping** — maps every threat to ATT&CK technique IDs automatically
- **AI Analyst** — explains any IP, domain, hash, or CVE in plain English using LLaMA 3.3

### Advanced Features
- **Redis Caching** — sub-millisecond lookups for frequent queries
- **Celery Scheduling** — automatic threat ingestion every hour
- **ML Anomaly Detection** — Isolation Forest algorithm detects unusual patterns
- **STIX2 Export** — industry-standard threat intelligence sharing format
- **PDF Reports** — downloadable threat intelligence reports
- **Threat Hunting** — proactive hunting by tag, MITRE technique, C2 infrastructure
- **IP Reputation Lookup** — instant cross-source reputation check
- **CVE Intelligence** — deep vulnerability analysis with CVSS scores
- **Email & Slack Alerts** — notifications when critical threats detected
- **REST API** — fully documented OpenAPI spec

---

## 🏗️ Architecture
External Feeds (AbuseIPDB, OTX, NVD)

↓

Ingestion Layer (Python + httpx + Celery)

↓

Normalization → PostgreSQL + Redis Cache

↓

Correlation Engine (Risk Scoring + MITRE ATT&CK)

↓

ML Anomaly Detection (Isolation Forest)

↓

AI Analyst Layer (Groq LLaMA 3.3)

↓

REST API (FastAPI) → React Dashboard

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL 15, Redis 7 |
| AI | Groq LLaMA 3.3 70B |
| ML | scikit-learn, Isolation Forest |
| Frontend | React, Recharts, Lucide |
| Task Queue | Celery, Celery Beat |
| Infrastructure | Docker, Docker Compose |
| Deployment | Render (backend), Vercel (frontend) |
| Standards | MITRE ATT&CK, STIX2.1, CVSS |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/threats` | Get all threats |
| GET | `/api/threats/search?q=` | Search threats |
| GET | `/api/threats/top/dangerous` | Top dangerous threats |
| GET | `/api/threats/filter/by-type/{type}` | Filter by type |
| GET | `/api/threats/stats` | Platform statistics |
| GET | `/api/threats/timeline/daily` | Daily threat timeline |
| POST | `/api/ingest/all` | Ingest from all sources |
| POST | `/api/correlate/run` | Run correlation engine |
| GET | `/api/correlate/alerts` | Get all alerts |
| GET | `/api/correlate/mitre/{id}` | MITRE mapping for threat |
| GET | `/api/ai/analyze/{id}` | AI analysis by ID |
| POST | `/api/ai/analyze` | AI analysis for any indicator |
| GET | `/api/ai/report` | Generate AI threat report |
| GET | `/api/ml/anomalies` | ML anomaly detection |
| GET | `/api/ml/anomalies/critical` | Critical anomalies only |
| GET | `/api/export/stix2` | Export as STIX2 bundle |
| GET | `/api/export/pdf` | Download PDF report |
| GET | `/api/export/summary` | Export summary stats |
| GET | `/api/lookup/ip/{ip}` | IP reputation lookup |
| GET | `/api/lookup/cve/{cve_id}` | CVE intelligence |
| GET | `/api/hunt/tag/{tag}` | Hunt by tag |
| GET | `/api/hunt/mitre/{technique}` | Hunt by MITRE technique |
| GET | `/api/hunt/high-risk-ips` | Hunt high risk IPs |
| GET | `/api/hunt/c2-infrastructure` | Hunt C2 infrastructure |
| GET | `/api/alerts/critical` | Get critical alerts |
| GET | `/api/cache/stats` | Redis cache statistics |
| DELETE | `/api/cache/clear` | Clear cache |

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
Create a `.env` file in the root:
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5455/threatlens

REDIS_URL=redis://localhost:6379

ABUSEIPDB_API_KEY=<get from abuseipdb.com/account/api>

ALIENVAULT_API_KEY=<get from otx.alienvault.com/settings>

GROQ_API_KEY=<get from console.groq.com/keys>

EMAIL_ADDRESS=<optional: gmail address for alerts>

EMAIL_PASSWORD=<optional: gmail app password>

ALERT_EMAIL=<optional: email to receive alerts>

SLACK_BOT_TOKEN=<optional: slack bot token>

SLACK_CHANNEL=<optional: slack channel id>

---

## 🔒 Security Standards
- MITRE ATT&CK Framework v14
- CVSS v3.1 Scoring
- STIX2.1 Threat Sharing Format
- CWE Weakness Classification

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 🐳 Docker

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Reset database
docker-compose down -v
docker-compose up -d
```

---

## 📁 Project Structure
ThreatLens/

├── app/

│   ├── ai/              ← AI analyst and report generation

│   ├── api/routes/      ← All API endpoints (10 routers)

│   ├── core/            ← Cache, ML, STIX2, alerting, hunting

│   ├── correlation/     ← Scoring, tagging, MITRE mapping

│   ├── db/              ← Database models and connection

│   └── ingestion/       ← AbuseIPDB, OTX, NVD fetchers

├── frontend/

│   └── src/             ← React dashboard

├── tests/               ← pytest test suite

├── docker-compose.yml

└── requirements.txt

---

## 👨‍💻 Author

**Subash Ramasubbu**
- GitHub: [@subash-ramasubbu](https://github.com/subash-ramasubbu)
- LinkedIn: [linkedin.com/in/subash-r-](https://www.linkedin.com/in/subash-r-)
- Live Demo: [threat-lens-theta.vercel.app](https://threat-lens-theta.vercel.app)

---

## ⭐ Star this repo if you found it useful!