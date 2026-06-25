from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_upload():
    csv_content = b"product_id,other_col\n12345,abc\n67890,def\n"
    file = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    response = client.post("/upload", files=file)
    print("Status Code:", response.status_code)
    print("Response:", response.json())

if __name__ == "__main__":
    test_upload()
