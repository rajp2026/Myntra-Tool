# app/services/product_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_product_details(product_id):

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    try:
        driver.get(f"https://www.myntra.com/{product_id}")

        brand = driver.find_element("class name", "pdp-title").text

        product_name = driver.find_element(
            "class name",
            "pdp-name"
        ).text

        return {
            "product_id": product_id,
            "brand": brand,
            "product_name": product_name
        }

    finally:
        driver.quit()