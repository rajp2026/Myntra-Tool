# Empty file
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def safe_get_text(driver, by, locator):
    try:
        return driver.find_element(by, locator).text.strip()
    except Exception:
        return None


def safe_wait_text(driver, by, locator, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        return element.text.strip()
    except Exception:
        return None


def get_product_details(driver, product_id):

    try:

        url = f"https://www.myntra.com/{product_id}"

        print(f"Opening : {url}")

        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "pdp-title")
            )
        )

        brand = safe_wait_text(driver, By.CLASS_NAME, "pdp-title")

        product_name = safe_wait_text(driver, By.CLASS_NAME, "pdp-name")

        description = safe_get_text(
            driver,
            By.CLASS_NAME,
            "pdp-product-description-content"
        )

        ratings_count = safe_get_text(
            driver,
            By.CLASS_NAME,
            "index-ratingsCount"
        )

        rating = None

        try:
            rating_container = driver.find_element(
                By.CLASS_NAME,
                "index-overallRating"
            )

            divs = rating_container.find_elements(By.TAG_NAME, "div")

            if divs:
                rating = divs[0].text.strip()

        except Exception:
            pass

        return {
            "product_id": product_id,
            "brand": brand,
            "product_name": product_name,
            "rating": rating,
            "ratings_count": ratings_count,
            "description": description,
        }

    except Exception as e:

        return {
            "product_id": product_id,
            "status": "failed",
            "error": str(e)
        }