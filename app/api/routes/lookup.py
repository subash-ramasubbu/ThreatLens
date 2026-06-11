from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.ip_lookup import full_ip_lookup

router = APIRouter(prefix="/api/lookup", tags=["Lookup"])


@router.get("/ip/{ip_address}")
def lookup_ip(ip_address: str, db: Session = Depends(get_db)):
    return full_ip_lookup(ip_address, db)