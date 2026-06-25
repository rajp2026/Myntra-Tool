from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
from app.services.csv_service import get_product_ids
from app.test.test_selenium import get_product_details
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>Myntra Product Tool</h1>
    <p>Server Running Successfully 🚀</p>
    """


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    product_ids = get_product_ids(file.file)

    return {
        "total_products": len(product_ids),
        "first_product": product_ids[0]
    }

@router.get("/test")
def test():

    result = get_product_details("35512522")

    return result