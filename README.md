# Myntra Product Scraper — Real-Time Streaming Edition

This is a complete, real-time scraping solution that extracts product details and category-sponsored ads from Myntra. It accepts a CSV file with product IDs as input and streams the results row-by-row to a modern React dashboard while persisting all data in a PostgreSQL database.

## 🚀 Tech Stack
- **Frontend**: React (Vite), Axios, Lucide React (Icons), Vanilla CSS
- **Backend**: FastAPI, WebSockets, `httpx` (Asynchronous HTTP), SQLAlchemy
- **Database**: PostgreSQL (`psycopg2-binary`)

---

## 🏗️ Architecture & Data Flow

This application is designed to be completely non-blocking, meaning users never have to sit and stare at a loading screen while waiting for an entire batch to finish. 

Here is the exact step-by-step flow of how data moves through the system:

1. **CSV Upload (Frontend -> Backend)**
   The user drops a CSV file into the React dashboard. The frontend makes a standard HTTP `POST` request to `/upload`. The backend parses the CSV, validates the `product_id` column, creates a unique `job_id`, and stores the pending IDs temporarily. It instantly returns the `job_id` to the frontend.
2. **WebSocket Handshake (Frontend <-> Backend)**
   Upon receiving the `job_id`, the frontend immediately opens a persistent WebSocket connection to `/ws/scrape/{job_id}`. 
3. **Database Initialization (Backend -> PostgreSQL)**
   The backend accepts the WebSocket connection and creates a new `ScrapeJob` record in the PostgreSQL database using SQLAlchemy.
4. **Asynchronous Scraping (`httpx` Generator)**
   The backend begins iterating over the pending product IDs. It uses `httpx.AsyncClient` to asynchronously fetch the raw HTML from Myntra. 
   - Instead of simulating a heavy headless browser, the scraper locates the embedded `window.__myx` JSON payload within the HTML source and extracts it. 
   - The scraping function is a native `async` generator. As soon as a product is parsed, it `yield`s the data object.
5. **Real-Time Streaming & Persistence**
   Inside the WebSocket route's `async for` loop, the moment a product or ad is yielded:
   - It is synchronously saved to PostgreSQL (`products` or `category_ads` tables) so it is never lost.
   - It is blasted across the WebSocket to the frontend using `await websocket.send_json(event)`.
6. **Dynamic Rendering (Frontend)**
   The React frontend receives the WebSocket message and performs a deep-copy state update. The newly scraped product is instantly appended to the UI table. The user watches the table populate row-by-row in real-time.
7. **Refresh Recovery**
   If the user refreshes the page, the frontend calls the `GET /history/latest` endpoint. The backend queries PostgreSQL for the most recent `ScrapeJob` and its associated products/ads, perfectly restoring the user's dashboard state.

---

## 🛠️ How to Run Locally

### Prerequisites
- Python 3.9+
- Node.js (for Vite frontend)
- PostgreSQL Server running locally (or via Docker)

### 1. Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Activate your virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend` directory and add your PostgreSQL credentials:
   ```env
   DATABASE_URL=postgresql://your_user:your_password@localhost:5432/myntra_db
   ```
5. Start the FastAPI server (SQLAlchemy will automatically create the tables on startup):
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### 2. Frontend Setup
1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open the provided `localhost` URL (usually `http://localhost:5173`) in your browser to access the dashboard!

---

## 🎯 Core Requirements Met

- **Detail Extraction**: Extracts Title, Description, Images (up to 2, heavily compressed CDN links replaced with high-res links), Rating, Ratings count, and a Category hierarchy string.
- **Category Ads**: Automatically parses the product's overarching category (e.g., "Handbags"), searches Myntra for that category, and returns exactly the first **3 sponsored (PLA) products**, including their rating and price.
- **Robustness**: 
  - Catches HTTP Timeouts, Connection Errors, and parses failures without crashing.
  - Handles HTTP `429 Too Many Requests` using an exponential backoff algorithm with jitter (`asyncio.sleep`).
  - Missing JSON keys gracefully fallback to `null` instead of throwing `KeyError`s.
- **Machine Readable Output**: A shiny **Download JSON** button on the frontend allows you to download the finalized scrape summary directly to your machine.

## 🔮 What I would build next with more time
1. **Proxy Rotation Pool:** While random delays and exponential backoffs are implemented, scraping 10,000+ items continuously would inevitably hit a hard IP block. Adding rotating residential proxies to `httpx` would make the tool enterprise-grade.
2. **Playwright for Delivery Check:** Myntra's delivery API is heavily protected by session tokens and internal signatures. To tackle the delivery estimation stretch goal robustly, I would implement an isolated worker running Playwright solely focused on validating pincodes on the product page.
