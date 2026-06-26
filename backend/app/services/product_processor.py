import time

from app.services.browser import get_driver
from app.services.product_scraper import get_product_details

import time

def scrape_with_retry(driver, product_id, retries=3):

    for attempt in range(retries):

        print(f"Attempt {attempt + 1}/{retries}")

        result = get_product_details(driver, product_id)

        # Success
        if result.get("status") != "failed":
            return result

        print("Retrying...")
        time.sleep(2)

    return result

def process_products(product_ids):

    driver = get_driver(headless=True)
    BATCH_SIZE = 25
    results = []

    total_start = time.perf_counter()

    try:

        total = len(product_ids)

        for index, product_id in enumerate(product_ids, start=1):
            if index > 1 and (index - 1) % BATCH_SIZE == 0:
                print("\nRestarting Browser...\n")
                driver.quit()
                driver = get_driver(headless=True)

            print(f"[{index}/{total}] Processing {product_id}")
            start = time.perf_counter()
            result = scrape_with_retry(driver, product_id)
            results.append(result)
            print(f"Completed in {time.perf_counter() - start:.2f}s")

        total_time = time.perf_counter() - total_start

        print("\n" + "=" * 70)
        print(f"Processed : {total}")
        print(f"Total Time : {total_time:.2f}s")
        print(f"Average    : {total_time / total:.2f}s/product")

        return results

    finally:

        driver.quit()