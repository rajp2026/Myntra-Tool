"""
FastAPI routes for the Myntra scraping backend.

Endpoints:
  POST /upload  — Upload a CSV with a ``product_id`` column.
  GET  /test    — Quick smoke test with 4 hardcoded product IDs.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.csv_service import get_product_ids
from app.services.api_scraper import process_products

router = APIRouter()


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Accept a CSV file, extract the ``product_id`` column, scrape
    every product, and return structured results with category ads.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are accepted.",
        )

    try:
        product_ids = get_product_ids(file.file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse CSV: {exc}",
        )

    if not product_ids:
        raise HTTPException(
            status_code=400,
            detail="No product IDs found in CSV.",
        )

    results = process_products(product_ids)
    return results


@router.get("/test")
def test():
    """Smoke test with 4 known product IDs."""
    product_ids = [
        "35512522",
        "31786093",
        "37403577",
        "27356632",
    ]
    results = process_products(product_ids)
    return results