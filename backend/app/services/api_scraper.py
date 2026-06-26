"""
Myntra Product Scraper
======================
Fetches product pages and category pages via HTTP, extracts the
embedded ``window.__myx`` JSON payload — no browser required.

Features:
  - Single-product detail extraction (images, rating, price, category …)
  - Category ad (PLA / sponsored) product extraction
  - Batch processing with rate-limit handling & exponential backoff
"""

import json
import time
import random
import re
import requests
from typing import Optional


# ──────────────────────────────────────────────
# Session helpers
# ──────────────────────────────────────────────

def _create_session() -> requests.Session:
    """Return a ``requests.Session`` with browser-like headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    })
    return session


# ──────────────────────────────────────────────
# JSON extraction from HTML
# ──────────────────────────────────────────────

def _extract_myx_data(html: str) -> Optional[dict]:
    """
    Locate the ``window.__myx = { … };`` block in the page source
    and return the parsed dictionary, or *None* on failure.
    """
    marker = "window.__myx = "
    idx = html.find(marker)
    if idx < 0:
        return None

    start = idx + len(marker)
    try:
        data, _ = json.JSONDecoder().raw_decode(html, start)
        return data
    except json.JSONDecodeError:
        return None


# ──────────────────────────────────────────────
# Image URL cleanup
# ──────────────────────────────────────────────

def _fix_image_url(url: str) -> str:
    """Replace Myntra CDN placeholders with concrete values."""
    url = re.sub(r"h_\(\$height\)", "h_720", url)
    url = re.sub(r"w_\(\$width\)",  "w_540", url)
    url = re.sub(r"q_\(\$qualityPercentage\)", "q_90", url)
    return url


# ──────────────────────────────────────────────
# Single-product fetch
# ──────────────────────────────────────────────

def get_product_details(
    session: requests.Session,
    product_id: str,
    retries: int = 3,
) -> dict:
    """
    Fetch ``https://www.myntra.com/{product_id}`` and return a dict
    with the product's metadata.

    On failure the dict contains ``"status": "failed"`` and an
    ``"error"`` message.
    """
    url = f"https://www.myntra.com/{product_id}"

    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=15)

            # ── Rate-limited ──
            if resp.status_code == 429:
                wait = min(2 ** attempt + random.uniform(0, 1), 30)
                print(f"  [429] Rate-limited on {product_id}. "
                      f"Retrying in {wait:.1f}s …")
                time.sleep(wait)
                continue

            # ── Non-200 ──
            if resp.status_code != 200:
                print(f"  [{resp.status_code}] Failed for {product_id}")
                return {
                    "product_id": product_id,
                    "status": "failed",
                    "error": f"HTTP {resp.status_code}",
                }

            # ── Parse embedded JSON ──
            myx = _extract_myx_data(resp.text)
            if not myx:
                print(f"  No embedded JSON for {product_id}")
                return {
                    "product_id": product_id,
                    "status": "failed",
                    "error": "No embedded JSON found",
                }

            pdp = myx.get("pdpData") or {}
            if not pdp:
                return {
                    "product_id": product_id,
                    "status": "failed",
                    "error": "No pdpData in response",
                }

            # ── Extract fields ──
            analytics   = pdp.get("analytics", {})
            rating_data = pdp.get("ratings", {}) or {}
            price_data  = pdp.get("price", {}) or {}

            # Title
            title = pdp.get("name", "")

            # Description
            desc = ""
            details_list = pdp.get("productDetails", [])
            if details_list:
                desc = details_list[0].get("description", "")

            # Images — first 2, with placeholders replaced
            images = []
            albums = pdp.get("media", {}).get("albums", [])
            if albums:
                raw_images = albums[0].get("images", [])
                for img in raw_images[:2]:
                    src = img.get("secureSrc", "")
                    if src:
                        images.append(_fix_image_url(src))

            # Rating
            rating = rating_data.get("averageRating")
            if rating is not None:
                rating = round(float(rating), 2)
            ratings_count = rating_data.get("totalCount")

            # Category string: articleType > subCategory > masterCategory
            article   = analytics.get("articleType", "")
            sub_cat   = analytics.get("subCategory", "")
            master    = analytics.get("masterCategory", "")
            gender    = analytics.get("gender", "")
            parts     = [p for p in [article, sub_cat, master, gender] if p]
            category  = " > ".join(parts) if parts else None

            # Brand
            brand = analytics.get("brand", "")

            # Price
            mrp              = price_data.get("mrp")
            discounted_price = price_data.get("discounted")

            return {
                "product_id":       product_id,
                "status":           "success",
                "title":            title,
                "brand":            brand,
                "description":      desc,
                "images":           images,
                "rating":           rating,
                "ratings_count":    ratings_count,
                "category":         category,
                "mrp":              mrp,
                "discounted_price": discounted_price,
            }

        except requests.exceptions.Timeout:
            print(f"  Timeout for {product_id} "
                  f"(attempt {attempt}/{retries})")
            time.sleep(2 ** attempt)

        except requests.exceptions.ConnectionError:
            print(f"  Connection error for {product_id} "
                  f"(attempt {attempt}/{retries})")
            time.sleep(2 ** attempt)

        except Exception as exc:
            print(f"  Unexpected error for {product_id} "
                  f"(attempt {attempt}/{retries}): {exc}")
            time.sleep(1)

    # Exhausted retries
    return {
        "product_id": product_id,
        "status": "failed",
        "error": "Max retries exceeded",
    }


# ──────────────────────────────────────────────
# Category ad (PLA / sponsored) fetch
# ──────────────────────────────────────────────

def get_category_ads(
    session: requests.Session,
    article_type: str,
    max_ads: int = 3,
) -> list[dict]:
    """
    Fetch the Myntra category search page for *article_type*
    (e.g. ``"handbags"``) and return up to *max_ads* PLA
    (sponsored) products.

    Each returned dict contains:
    ``product_id, name, brand, rating, price, mrp, image``.

    Returns an empty list on any error or if there are no PLA
    products.
    """
    # Normalise: lowercase, replace spaces with hyphens
    slug = article_type.lower().replace(" ", "-")
    url  = f"https://www.myntra.com/{slug}"

    try:
        resp = session.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"  Category fetch [{resp.status_code}] for '{slug}'")
            return []

        myx = _extract_myx_data(resp.text)
        if not myx:
            print(f"  No embedded JSON on category page '{slug}'")
            return []

        results = (
            myx.get("searchData", {})
               .get("results", {})
        )

        pla_products = results.get("plaProducts", []) or []

        ads = []
        for item in pla_products[:max_ads]:
            ads.append({
                "product_id": str(item.get("productId", "")),
                "name":       item.get("product", item.get("productName", "")),
                "brand":      item.get("brand", ""),
                "rating":     item.get("rating", None),
                "price":      item.get("price", None),
                "mrp":        item.get("mrp", None),
                "image":      item.get("searchImage", ""),
                "is_sponsored": True,
            })

        return ads

    except Exception as exc:
        print(f"  Error fetching category ads for '{slug}': {exc}")
        return []


# ──────────────────────────────────────────────
# Batch processing
# ──────────────────────────────────────────────

def process_products(
    product_ids: list[str],
    product_delay: tuple[float, float] = (0.3, 1.0),
    category_delay: tuple[float, float] = (0.5, 1.0),
) -> dict:
    """
    Scrape a batch of Myntra products and their category ads.

    Returns::

        {
            "products":      [ … ],
            "category_ads":  { "Handbags": [ … ], … },
            "summary": {
                "total":        int,
                "successful":   int,
                "failed":       int,
                "time_seconds": float,
            },
        }
    """
    session  = _create_session()
    products = []
    categories_seen: set[str] = set()

    total      = len(product_ids)
    successful = 0
    failed     = 0
    t_start    = time.perf_counter()

    # ── Fetch every product ──
    for idx, pid in enumerate(product_ids, 1):
        print(f"[{idx}/{total}] Fetching product {pid} …")
        t0 = time.perf_counter()

        result = get_product_details(session, pid)
        products.append(result)

        if result.get("status") == "failed":
            failed += 1
            print(f"  FAILED in {time.perf_counter() - t0:.2f}s")
        else:
            successful += 1
            print(f"  OK in {time.perf_counter() - t0:.2f}s")

            # Collect unique articleType for category-ad lookup
            cat = result.get("category", "")
            if cat:
                # articleType is the first segment before " > "
                article = cat.split(" > ")[0].strip()
                if article:
                    categories_seen.add(article)

        # Random inter-request delay (skip after last)
        if idx < total:
            time.sleep(random.uniform(*product_delay))

    # ── Fetch category ads for each unique articleType ──
    category_ads: dict[str, list[dict]] = {}
    cat_list = sorted(categories_seen)

    for idx, cat in enumerate(cat_list, 1):
        print(f"[Cat {idx}/{len(cat_list)}] Fetching ads for '{cat}' …")
        ads = get_category_ads(session, cat)
        category_ads[cat] = ads
        print(f"  Found {len(ads)} sponsored product(s)")

        if idx < len(cat_list):
            time.sleep(random.uniform(*category_delay))

    elapsed = round(time.perf_counter() - t_start, 2)

    # ── Summary ──
    print("\n" + "=" * 60)
    print(f"Products   : {successful}/{total} successful")
    print(f"Categories : {len(cat_list)} scanned")
    print(f"Total time : {elapsed}s")

    return {
        "products": products,
        "category_ads": category_ads,
        "summary": {
            "total":        total,
            "successful":   successful,
            "failed":       failed,
            "categories":   len(cat_list),
            "time_seconds": elapsed,
        },
    }
