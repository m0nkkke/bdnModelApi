import os
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_predict_endpoint():
    test_image_path = os.path.join(os.path.dirname(__file__), "sample.jpg")
    assert os.path.exists(test_image_path), "tests/sample.jpg для теста"

    with open(test_image_path, "rb") as f:
        response = client.post(
            "/predict",
            files={"file": ("sample.jpg", f, "image/jpeg")}
        )
    assert response.status_code == 200, response.text

    data = response.json()
    assert "barcodes" in data
    assert "items" in data
    assert isinstance(data["barcodes"], list)
    assert isinstance(data["items"], list)
