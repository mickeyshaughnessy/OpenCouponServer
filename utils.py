import time, redis, config, requests, json
from unittest.mock import patch, MagicMock

redis_client = redis.StrictRedis()

def match_coupons(context, chatbot_id, token, n_coupons=5, get_images=True, api_url="https://api.beavis.com/GET_COUPONS"):
    payload = {
        "chatbot_id": chatbot_id,
        "token": token,
        "context": context[:2000],
        "N_COUPONS": n_coupons,
        "GET_IMAGES": get_images
    }
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("coupons", [])
    except requests.RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        return []
    except json.JSONDecodeError:
        print("Failed to decode the API response as JSON.")
        return []

def auth_req(req):
    account_id, key = req.get("account_id"), req.get("key")
    acc = redis_client.hget(config.REDHASH_ACCOUNT, account_id)
    if acc:
        pkey = json.loads(acc).get("pkey")
        return pkey == key
    return False

def run_tests():
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "coupons": [
                {"text": "10% off electronics", "image_url": "http://example.com/coupon1.jpg"},
                {"text": "Buy one get one free on appliances", "image_url": "http://example.com/coupon2.jpg"}
            ]
        }
        mock_post.return_value = mock_response

        result = match_coupons("electronics deals", "test_chatbot", "test_token")
        assert len(result) == 2, f"Expected 2 coupons, got {len(result)}"
        assert result[0]["text"] == "10% off electronics", f"Unexpected coupon text: {result[0]['text']}"
        print("match_coupons test passed")

    with patch.object(redis_client, 'hget') as mock_hget:
        mock_hget.return_value = json.dumps({"pkey": "valid_key"})
        
        valid_req = {"account_id": "test_account", "key": "valid_key"}
        assert auth_req(valid_req) == True, "Authentication should succeed with valid key"
        
        invalid_req = {"account_id": "test_account", "key": "invalid_key"}
        assert auth_req(invalid_req) == False, "Authentication should fail with invalid key"
        
        print("auth_req test passed")

if __name__ == "__main__":
    print("Running tests...")
    run_tests()
    
    print("\nDemo of match_coupons (this will make a real API call):")
    context = "Looking for deals on electronics and home appliances"
    chatbot_id, token = "your_chatbot_id", "your_api_token"
    matched_coupons = match_coupons(context, chatbot_id, token)
    for coupon in matched_coupons:
        print(f"Coupon: {coupon['text']}")
        print(f"Image URL: {coupon['image_url']}")
        print("---")