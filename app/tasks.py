from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.ingestion.abuseipdb import fetch_abuseipdb
from app.ingestion.alienvault import fetch_alienvault
from app.ingestion.nvd import fetch_nvd_cves
from app.correlation.engine import run_correlation
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.fetch_all_threats")
def fetch_all_threats():
    db = SessionLocal()
    try:
        logger.info("Starting scheduled threat ingestion...")

        abuse_result = fetch_abuseipdb(db)
        logger.info(f"AbuseIPDB: {abuse_result}")

        otx_result = fetch_alienvault(db)
        logger.info(f"AlienVault OTX: {otx_result}")

        nvd_result = fetch_nvd_cves(db)
        logger.info(f"NVD: {nvd_result}")

        total_saved = (
            abuse_result.get("saved", 0) +
            otx_result.get("saved", 0) +
            nvd_result.get("saved", 0)
        )

        logger.info(f"Total new threats saved: {total_saved}")
        return {
            "abuseipdb": abuse_result,
            "alienvault": otx_result,
            "nvd": nvd_result,
            "total_saved": total_saved,
        }

    except Exception as e:
        logger.error(f"Error in fetch_all_threats: {e}")
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.run_correlation_task")
def run_correlation_task():
    db = SessionLocal()
    try:
        logger.info("Starting scheduled correlation...")
        result = run_correlation(db)
        logger.info(f"Correlation complete: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in run_correlation_task: {e}")
        return {"error": str(e)}
    finally:
        db.close()


@celery_app.task(name="app.tasks.manual_fetch")
def manual_fetch():
    return fetch_all_threats()