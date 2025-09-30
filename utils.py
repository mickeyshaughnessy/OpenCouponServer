"""
Utility functions for the Beavis API server.
"""

import json
import requests
from typing import Dict, List
from s3_storage import S3Storage

storage = S3Storage()

def auth_req(req: Dict) -> bool:
    """
    Authenticate a request using account credentials.
    Supports chatbot (chatbot_id + token) and advertiser (account_id + key) auth.
    """
    chatbot_id = req.get("chatbot_id")
    token = req.get("token")
    
    if chatbot_id and token:
        return authenticate_chatbot(chatbot_id, token)
    
    account_id = req.get("account_id")
    key = req.get("key")
    
    if account_id and key:
        return authenticate_advertiser(account_id, key)
    
    return False

def authenticate_chatbot(chatbot_id: str, token: str) -> bool:
    """Authenticate a chatbot using chatbot_id and token."""
    try:
        account_data = storage.get_account(chatbot_id)
        if not account_data:
            return False
        return account_data.get("token") == token
    except Exception:
        return False

def authenticate_advertiser(account_id: str, key: str) -> bool:
    """Authenticate an advertiser using account_id and key."""
    try:
        account_data = storage.get_account(account_id)
        if not account_data:
            return False
        stored_key = account_data.get("pkey") or account_data.get("key")
        return stored_key == key
    except Exception:
        return False

def match_coupons(
    context: str,
    chatbot_id: str,
    token: str,
    n_coupons: int = 5,
    get_images: bool = True,
    api_url: str = "http://localhost:8050/GET_COUPONS"
) -> List[Dict]:
    """
    Client function to retrieve coupons from the Beavis API.
    """
    payload = {
        "chatbot_id": chatbot_id,
        "token": token,
        "context": context[:2000],
        "N_COUPONS": n_coupons,
        "GET_IMAGES": get_images
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("coupons", [])
    except Exception as e:
        print(f"API request error: {e}")
        return []

def create_test_account(account_id: str, key: str, account_type: str = "advertiser") -> bool:
    """Create a test account in S3 for development/testing."""
    try:
        account_data = {
            "account_id": account_id,
            "type": account_type
        }
        
        if account_type == "chatbot":
            account_data["token"] = key
        else:
            account_data["pkey"] = key
        
        storage.save_account(account_id, account_data)
        return True
    except Exception as e:
        print(f"Failed to create account: {e}")
        return False