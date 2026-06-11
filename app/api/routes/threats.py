from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import ThreatIndicator
from app.api.schemas import ThreatCreate, ThreatResponse, ThreatUpdate
from app.core.cache import get_cached, set_cached, delete_cached, clear_threats_cache

router = APIRouter(prefix="/api/threats", tags=["Threats"])


@router.post("/", response_model=ThreatResponse)
def create_threat(threat: ThreatCreate, db: Session = Depends(get_db)):
    existing = db.query(ThreatIndicator).filter(
        ThreatIndicator.value == threat.value
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Threat indicator already exists")

    db_threat = ThreatIndicator(**threat.dict())
    db.add(db_threat)
    db.commit()
    db.refresh(db_threat)

    clear_threats_cache()
    return db_threat


@router.get("/", response_model=List[ThreatResponse])
def get_all_threats(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    cache_key = f"threat:all:{skip}:{limit}:{severity}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    query = db.query(ThreatIndicator)
    if severity:
        query = query.filter(ThreatIndicator.severity == severity)
    threats = query.offset(skip).limit(limit).all()

    result = [
        {
            "id": t.id,
            "type": t.type,
            "value": t.value,
            "severity": t.severity,
            "confidence": t.confidence,
            "risk_score": t.risk_score,
            "source": t.source,
            "tags": t.tags,
            "description": t.description,
            "country": t.country,
            "first_seen": t.first_seen,
            "last_seen": t.last_seen,
            "created_at": t.created_at,
        }
        for t in threats
    ]

    set_cached(cache_key, result)
    return threats


@router.get("/search", response_model=List[ThreatResponse])
def search_threats(q: str, db: Session = Depends(get_db)):
    cache_key = f"threat:search:{q}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    results = db.query(ThreatIndicator).filter(
        ThreatIndicator.value.contains(q) |
        ThreatIndicator.tags.contains(q) |
        ThreatIndicator.description.contains(q)
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="No threats found")

    set_cached(cache_key, [r.__dict__ for r in results], ttl=300)
    return results


@router.get("/stats")
def get_threat_stats(db: Session = Depends(get_db)):
    cache_key = "threat:stats"
    cached = get_cached(cache_key)
    if cached:
        return cached

    total = db.query(ThreatIndicator).count()
    critical = db.query(ThreatIndicator).filter(
        ThreatIndicator.risk_score >= 85
    ).count()
    high = db.query(ThreatIndicator).filter(
        ThreatIndicator.risk_score >= 65,
        ThreatIndicator.risk_score < 85
    ).count()
    medium = db.query(ThreatIndicator).filter(
        ThreatIndicator.risk_score >= 40,
        ThreatIndicator.risk_score < 65
    ).count()

    from collections import Counter
    all_threats = db.query(ThreatIndicator).all()
    sources = dict(Counter(t.source for t in all_threats).most_common(5))

    result = {
        "total": total,
        "critical": critical,
        "high": high,
        "medium": medium,
        "sources": sources,
    }

    set_cached(cache_key, result, ttl=300)
    return result


@router.get("/{threat_id}", response_model=ThreatResponse)
def get_threat(threat_id: int, db: Session = Depends(get_db)):
    cache_key = f"threat:{threat_id}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    set_cached(cache_key, {
        "id": threat.id,
        "type": threat.type,
        "value": threat.value,
        "severity": threat.severity,
        "confidence": threat.confidence,
        "risk_score": threat.risk_score,
        "source": threat.source,
        "tags": threat.tags,
        "description": threat.description,
        "country": threat.country,
        "first_seen": threat.first_seen,
        "last_seen": threat.last_seen,
        "created_at": threat.created_at,
    })
    return threat


@router.patch("/{threat_id}", response_model=ThreatResponse)
def update_threat(
    threat_id: int,
    updates: ThreatUpdate,
    db: Session = Depends(get_db)
):
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    for field, value in updates.dict(exclude_none=True).items():
        setattr(threat, field, value)

    db.commit()
    db.refresh(threat)

    delete_cached(f"threat:{threat_id}")
    clear_threats_cache()
    return threat


@router.delete("/{threat_id}")
def delete_threat(threat_id: int, db: Session = Depends(get_db)):
    threat = db.query(ThreatIndicator).filter(
        ThreatIndicator.id == threat_id
    ).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")

    db.delete(threat)
    db.commit()

    delete_cached(f"threat:{threat_id}")
    clear_threats_cache()
    return {"message": f"Threat {threat_id} deleted successfully"}

@router.get("/filter/by-type/{threat_type}", response_model=List[ThreatResponse])
def filter_by_type(threat_type: str, db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.type == threat_type
    ).order_by(ThreatIndicator.risk_score.desc()).all()
    if not threats:
        raise HTTPException(status_code=404, detail=f"No {threat_type} threats found")
    return threats


@router.get("/filter/by-score", response_model=List[ThreatResponse])
def filter_by_score(
    min_score: float = 0,
    max_score: float = 100,
    db: Session = Depends(get_db)
):
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.risk_score >= min_score,
        ThreatIndicator.risk_score <= max_score
    ).order_by(ThreatIndicator.risk_score.desc()).all()
    return threats


@router.get("/filter/by-country/{country}", response_model=List[ThreatResponse])
def filter_by_country(country: str, db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).filter(
        ThreatIndicator.country == country.upper()
    ).order_by(ThreatIndicator.risk_score.desc()).all()
    if not threats:
        raise HTTPException(status_code=404, detail=f"No threats from {country}")
    return threats


@router.get("/top/dangerous", response_model=List[ThreatResponse])
def get_top_dangerous(limit: int = 10, db: Session = Depends(get_db)):
    threats = db.query(ThreatIndicator).order_by(
        ThreatIndicator.risk_score.desc()
    ).limit(limit).all()
    return threats