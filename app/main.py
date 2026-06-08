from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db
from app.api.routes import threats, ingestion, correlation, ai, cache, export
from app.api.routes import threats, ingestion, correlation, ai, cache, export, alerts
from app.api.routes import threats, ingestion, correlation, ai, cache, export, alerts, ml

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered threat intelligence platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(threats.router)
app.include_router(ingestion.router)
app.include_router(correlation.router)
app.include_router(ai.router)
app.include_router(cache.router)
app.include_router(export.router)
app.include_router(alerts.router)
app.include_router(ml.router)

@app.get("/")
def root():
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}