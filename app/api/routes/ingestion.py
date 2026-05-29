from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.ingestion.abuseipdb import fetch_abuseipdb
from app.ingestion.alienvault import fetch_alienvault
from app.ingestion.nvd import fetch_nvd_cves

router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])


@router.post("/abuseipdb")
def ingest_abuseipdb(db: Session = Depends(get_db)):
    result = fetch_abuseipdb(db)
    return {"source": "abuseipdb", "result": result}


@router.post("/alienvault")
def ingest_alienvault(db: Session = Depends(get_db)):
    result = fetch_alienvault(db)
    return {"source": "alienvault", "result": result}


@router.post("/nvd")
def ingest_nvd(db: Session = Depends(get_db)):
    result = fetch_nvd_cves(db)
    return {"source": "nvd", "result": result}


@router.post("/all")
def ingest_all(db: Session = Depends(get_db)):
    abuse = fetch_abuseipdb(db)
    otx = fetch_alienvault(db)
    nvd = fetch_nvd_cves(db)
    return {
        "abuseipdb": abuse,
        "alienvault": otx,
        "nvd": nvd,
    }