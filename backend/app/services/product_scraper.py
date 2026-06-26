import time
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def safe_get_text(driver, by, locator):
    try:
        return driver.find_element(by, locator).text.strip()
    except Exception:
        return None


def safe_wait_text(driver, by, locator, timeout=2):
    """
    Wait only 2 seconds.
    If not found, return None.
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        return element.text.strip()
    except Exception:
        return None


# --------------------------------------------------
# Main Scraper
# --------------------------------------------------

def get_product_details(driver, product_id):

    try:

        url = f"https://www.myntra.com/{product_id}"

        print("\n" + "=" * 60)
        print(f"Opening : {url}")

        # ---------------------------------
        # PAGE LOAD
        # ---------------------------------

        start = time.perf_counter()

        driver.get(url)
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)


        print(f"driver.get() : {time.perf_counter() - start:.2f}s")
        print("Current URL :", driver.current_url)
        print("Page Title  :", driver.title)
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        # ---------------------------------
        # WAIT FOR PAGE
        # ---------------------------------

        start = time.perf_counter()

        # WebDriverWait(driver, 5).until(
        #     EC.presence_of_element_located(
        #         (By.CLASS_NAME, "pdp-title")
        #     )
        # )

        WebDriverWait(driver, 15).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "pdp-title")) > 0
        )
        print("Title:", driver.title)
        print("URL:", driver.current_url)
        print("pdp-title found:", len(driver.find_elements(By.CLASS_NAME, "pdp-title")))
        print(f"Initial Wait : {time.perf_counter() - start:.2f}s")

        # ---------------------------------
        # BRAND
        # ---------------------------------

        start = time.perf_counter()

        brand = safe_wait_text(
            driver,
            By.CLASS_NAME,
            "pdp-title"
        )

        print(f"Brand : {time.perf_counter() - start:.2f}s")

        # ---------------------------------
        # PRODUCT NAME
        # ---------------------------------

        start = time.perf_counter()

        product_name = safe_wait_text(
            driver,
            By.CLASS_NAME,
            "pdp-name"
        )

        print(f"Product Name : {time.perf_counter() - start:.2f}s")

        # ---------------------------------
        # DESCRIPTION
        # ---------------------------------

        start = time.perf_counter()

        description = safe_get_text(
            driver,
            By.CLASS_NAME,
            "pdp-product-description-content"
        )

        print(f"Description : {time.perf_counter() - start:.2f}s")

        # ---------------------------------
        # RATINGS COUNT
        # ---------------------------------

        start = time.perf_counter()

        ratings_count = safe_get_text(
            driver,
            By.CLASS_NAME,
            "index-ratingsCount"
        )

        print(f"Ratings Count : {time.perf_counter() - start:.2f}s")

        # ---------------------------------
        # RATING
        # ---------------------------------

        start = time.perf_counter()

        rating = None

        try:

            rating_container = driver.find_element(
                By.CLASS_NAME,
                "index-overallRating"
            )

            divs = rating_container.find_elements(
                By.TAG_NAME,
                "div"
            )

            if divs:
                rating = divs[0].text.strip()

        except Exception:
            pass

        print(f"Rating : {time.perf_counter() - start:.2f}s")

        print("Finished Successfully")

        return {
            "product_id": product_id,
            "brand": brand,
            "product_name": product_name,
            "rating": rating,
            "ratings_count": ratings_count,
            "description": description,
        }

    except Exception as e:

        print("\nERROR OCCURRED")
        traceback.print_exc()

        return {
            "product_id": product_id,
            "status": "failed",
            "error": str(e)
        }