from fastapi import APIRouter, UploadFile, File
from app.services.product_processor import process_products

from app.services.browser import get_driver
from app.services.product_scraper import get_product_details
from app.services.csv_service import get_product_ids
router = APIRouter()

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):

    product_ids = get_product_ids(file.file)

    results = process_products(product_ids)

    return results

@router.get("/test")
def test():

    driver = get_driver()

    try:

        product_ids = [
            "35512522",
            "31786093",
            "37403577",
            "27356632"
        ]

        results = []

        for product_id in product_ids:

            print("=" * 50)
            print(product_id)

            result = get_product_details(driver, product_id)

            results.append(result)

        return results

    finally:

        driver.quit()