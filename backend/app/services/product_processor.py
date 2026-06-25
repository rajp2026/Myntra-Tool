from app.services.browser import get_driver
from app.services.product_scraper import get_product_details


def process_products(product_ids):

    driver = get_driver(headless=True)

    results = []

    try:

        total = len(product_ids)

        for index, product_id in enumerate(product_ids, start=1):

            print(f"[{index}/{total}] Processing {product_id}")

            result = get_product_details(driver, product_id)

            results.append(result)

        return results

    finally:

        driver.quit()