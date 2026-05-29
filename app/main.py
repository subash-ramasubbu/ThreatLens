from fastapi import FastAPI
from app.core.config import settings
from app.db.init_db import init_db
from app.api.routes import threats, ingestion

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered threat intelligence platform",
)

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(threats.router)
app.include_router(ingestion.router)

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