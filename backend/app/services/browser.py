from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(headless=True):

    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    # -----------------------------------------------
    # Anti-detection: make Selenium look like a real
    # browser so Myntra doesn't block the request.
    # -----------------------------------------------

    # Remove automation flags
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Real user-agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    # Standard browser window size
    options.add_argument("--window-size=1920,1080")

    # Don't wait for every image/font to load
    options.page_load_strategy = "eager"

    # Disable image downloading (speed optimization)
    prefs = {
        "profile.managed_default_content_settings.images": 2
    }

    options.add_experimental_option("prefs", prefs)

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # Override navigator.webdriver to false
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        },
    )

    return driver