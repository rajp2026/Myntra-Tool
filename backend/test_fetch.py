import requests
import json

s = requests.Session()
s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.myntra.com/35512522",
    "Origin": "https://www.myntra.com",
})

# Try delivery API - common patterns
product_id = "35512522"
pincodes = {
    "Bengaluru": "560001",
    "Mumbai": "400001", 
    "Delhi": "110001",
    "Ahmedabad": "380001",
    "Kolkata": "700001",
}

# First, get the product page to pick up cookies
r = s.get(f"https://www.myntra.com/{product_id}", timeout=10)
print(f"Product page status: {r.status_code}")
print(f"Cookies: {dict(s.cookies)}")

# Try delivery estimation endpoint
for city, pincode in pincodes.items():
    urls_to_try = [
        f"https://www.myntra.com/gateway/v2/delivery/estimate?styleId={product_id}&pincode={pincode}",
        f"https://www.myntra.com/gateway/v1/serviceability?styleId={product_id}&pincode={pincode}",
    ]
    for url in urls_to_try:
        try:
            r = s.get(url, timeout=5)
            if r.status_code == 200:
                print(f"\n{city} ({pincode}): {url}")
                print(json.dumps(r.json(), indent=2)[:500])
                break
            else:
                print(f"{city} ({pincode}): {r.status_code} - {url}")
        except Exception as e:
            print(f"{city} ({pincode}): Error - {e}")
