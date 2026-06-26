# Myntra Product Scraper

This is a complete backend and frontend solution for scraping product details and category-sponsored ads from Myntra, taking a CSV file with product IDs as input.

## How to run it

### Prerequisites
- Python 3.9+
- A virtual environment is recommended.

### 1. Backend Setup & Run
1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Activate your virtual environment (if not already active). For Windows:
   ```bash
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn requests pandas python-multipart
   ```
4. Start the server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### 2. Frontend Access
Once the server is running, the application serves the static frontend directly! 
Open your browser and navigate to:
**http://localhost:8000/app/**

You will see a premium drag-and-drop interface where you can upload your CSV file and view the results in an elegant card layout. 
You can download a **Sample CSV** from the frontend to test the tool immediately.

## The Approach and Why
Initially, the scraper relied on Selenium because many modern websites use complex Javascript rendering to load product data. However, Myntra implements robust bot protection that quickly detects and blocks headless browsers, serving them an offline dinosaur game page instead of the actual product catalog. 

**The Solution:**
I shifted to an API/HTML-extraction approach. By examining the raw HTML served by Myntra, I discovered that they embed the entire product details and search payload as a JSON object inside `window.__myx`.
Instead of simulating a browser, this backend directly requests the page source using `requests` (with browser-like headers) and extracts this JSON payload. 

**Benefits of this approach:**
- **Incredibly Fast:** Bypasses browser rendering entirely. What took ~15 minutes with Selenium now takes ~1.5 minutes for 100 products.
- **Rich Data:** Gives structured access to everything Myntra has (detailed ratings count, full taxonomy, image variants, discount logic).
- **Stealthy & Reliable:** Less prone to driver crashes, and easier to manage concurrency and exponential backoffs when Myntra rate-limits the IP.

## Assumptions Made
1. **Data Availability:** The structure of `window.__myx` is assumed to remain relatively stable. If Myntra updates its frontend framework significantly, the JSON extraction logic may need adjustments.
2. **Rate Limits:** To avoid being blocked, a randomized delay is inserted between requests (0.3s - 1.0s), along with an exponential backoff specifically handling `429 Too Many Requests` status codes.
3. **Category Ads Mapping:** "Category" in the context of the ads means the `articleType` (e.g., "Handbags", "Messenger Bag"). The tool grabs the first 3 Product Listing Ads (PLA) for every unique `articleType` found in the uploaded batch.

## Scoped In vs Out

**Scoped In (Core Requirements Met):**
- Extracts Title, Description, Images (up to 2 with corrected resolutions), Rating, Ratings count, and a Category hierarchy string.
- Automatically groups and fetches the top 3 sponsored/ad products for each unique category derived from the given product IDs.
- Robust exception handling and retry mechanisms. Missing data yields a `null`/fallback rather than crashing the script.
- A beautiful, responsive Frontend built with pure HTML/CSS/JS (no framework needed). Allows CSV upload, real-time fetching indication, visualization of results, and downloading the output as a clean JSON file.

**Scoped Out (Stretch Goals):**
- **Delivery check by Pincode:** Scoped out. After investigation, Myntra's delivery API is heavily protected by session tokens, internal signatures, and CORS restrictions. Calling it programmatically without an active, cookie-heavy session results in `404` or `401 Unauthorized`. To build this robustly would require intercepting internal XHR requests using a headless browser (like Playwright), which drastically impacts the speed of the script. Given the "two days" time budget, prioritizing a rock-solid, fast core scraper over a brittle, slow delivery feature was chosen.

## What I would build next with more time
1. **Asynchronous Scraping (Celery / Redis):** Instead of keeping the HTTP request open while 100 products are fetched sequentially (which could lead to browser timeouts), I would implement a job queue. The frontend would receive a `job_id` and poll for progress, or rely on WebSockets for real-time card population.
2. **Proxy Rotation Pool:** While random delays and exponential backoffs are implemented, scraping 10,000+ items would inevitably hit a hard IP block. Adding rotating residential proxies would make the tool enterprise-grade.
3. **Asyncio Requests:** Fetching the products using `aiohttp` or `httpx` concurrently (in small batches of 3-5) would significantly cut down total processing time while still remaining under the radar. 
4. **Playwright for Delivery Check:** To tackle the delivery estimation stretch goal, I would implement an isolated worker running Playwright solely focused on validating pincodes on the product page.
