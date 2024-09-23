import time, redis, config

redis = redis.StrictRedis()

import requests
import json

def match_coupons(context, chatbot_id, token, n_coupons=5, get_images=True, api_url="https://api.beavis.com/GET_COUPONS"):
    """
    Match coupons from the Beavis API based on the given context.

    Args:
    context (str): The context for coupon matching (up to 2000 characters).
    chatbot_id (str): The ID of the chatbot.
    token (str): Authentication token for the API.
    n_coupons (int, optional): Number of coupons to request. Defaults to 5.
    get_images (bool, optional): Whether to request coupon images. Defaults to True.
    api_url (str, optional): The URL of the Beavis API endpoint. Defaults to "https://api.beavis.com/GET_COUPONS".

    Returns:
    list: A list of dictionaries containing matched coupons with their text and image URLs.
    """
    # Prepare the request payload
    payload = {
        "chatbot_id": chatbot_id,
        "token": token,
        "context": context[:2000],  # Ensure context doesn't exceed 2000 characters
        "N_COUPONS": n_coupons,
        "GET_IMAGES": get_images
    }

    try:
        # Make the API request
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the JSON response
        data = response.json()

        # Extract and return the coupons
        return data.get("coupons", [])

    except requests.RequestException as e:
        print(f"An error occurred while making the API request: {e}")
        return []

    except json.JSONDecodeError:
        print("Failed to decode the API response as JSON.")
        return []


def auth_req(req):
    account_id = req.get("account_id")
    key = req.get("key")
    acc = redis.hget(config.REDHASH_ACCOUNT, account_id)
    if acc:
        acc.get("pkey")
        _now = int(time.time())

if __name__ == "__main__":
    context = "Looking for deals on electronics and home appliances"
    chatbot_id = "your_chatbot_id"
    token = "your_api_token"

    matched_coupons = match_coupons(context, chatbot_id, token)

    for coupon in matched_coupons:
        print(f"Coupon: {coupon['text']}")
        print(f"Image URL: {coupon['image_url']}")
        print("---")
