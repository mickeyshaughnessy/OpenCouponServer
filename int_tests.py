import requests, json
from unittest.mock import patch

BASE_URL = "http://localhost:8050"

def test_make_coupons():
    payload = {
        "account_id": "business_123",
        "key": "valid_key",
        "coupons": [
            {"text_body": "50% off on all items!", "bid_price": 0.7},
            {"text_body": "Free shipping on orders over $50", "bid_price": 0.5}
        ]
    }
    with patch('utils.auth_req', return_value=True):
        response = requests.post(f"{BASE_URL}/MAKE_COUPONS", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "error" not in data
        assert "coupon_ids" in data
        print("MAKE_COUPONS test passed")

def test_get_coupons():
    payload = {
        "account_id": "user_123",
        "key": "valid_key",
        "context": "Looking for discounts on clothing",
        "N_COUPONS": 3
    }
    with patch('utils.auth_req', return_value=True), \
         patch('api_server.redis_client.hvals', return_value=[
             json.dumps({
                 "coupon_id": "1",
                 "account_id": "business_123",
                 "text_body": "50% off on all clothing!",
                 "bid_price": 0.7,
                 "timestamp": 1630000000
             }),
             json.dumps({
                 "coupon_id": "2",
                 "account_id": "business_456",
                 "text_body": "Discounts on electronics.",
                 "bid_price": 0.3,
                 "timestamp": 1630000001
             })
         ]), \
         patch('llm.make_completion', return_value="0.9"):
        response = requests.post(f"{BASE_URL}/GET_COUPONS", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "error" not in data
        assert len(data["coupons"]) == 2
        print("GET_COUPONS test passed")

if __name__ == "__main__":
    test_make_coupons()
    test_get_coupons()
    print("All integration tests passed")