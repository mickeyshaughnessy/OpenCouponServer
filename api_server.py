"""
Beavis Open Coupon Server API
Provides endpoints for advertisers to upload coupons and chatbots to retrieve them.
Uses S3 for persistent storage.
"""

import json
import uuid
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import auth_req
from llm import generate_completion
from s3_storage import S3Storage
import config

# Initialize
storage = S3Storage()
app = Flask(__name__)
CORS(app)

@app.route("/GET_COUPONS", methods=['POST'])
def get_coupons_route():
    """Endpoint for chatbots to retrieve contextually relevant coupons."""
    try:
        req = request.get_json()
        if not req:
            return jsonify({"error": "Invalid JSON"}), 400
        
        result = get_coupons(req)
        if "error" in result:
            return jsonify(result), 401 if result["error"] == "Authentication failed" else 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/MAKE_COUPONS", methods=['POST'])
def make_coupons_route():
    """Endpoint for advertisers to upload coupons."""
    try:
        req = request.get_json()
        if not req:
            return jsonify({"error": "Invalid JSON"}), 400
        
        result = make_coupons(req)
        if "error" in result:
            return jsonify(result), 401 if result["error"] == "Authentication failed" else 400
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def make_coupons(req):
    """Create and store coupons from advertisers."""
    if not auth_req(req):
        return {"error": "Authentication failed"}
    
    account_id = req.get("account_id")
    coupons = req.get("coupons", [])
    
    if not coupons or not isinstance(coupons, list):
        return {"error": "No coupons provided"}
    
    coupon_ids = []
    
    for coupon in coupons:
        if not isinstance(coupon, dict):
            continue
            
        text_body = coupon.get("text_body", "")
        bid_price = coupon.get("bid_price", 0)
        
        if not text_body or bid_price <= 0:
            continue
        
        if len(text_body) > config.MAX_COUPON_TEXT_LENGTH:
            text_body = text_body[:config.MAX_COUPON_TEXT_LENGTH]
        
        coupon_id = str(uuid.uuid4())
        coupon_data = {
            "coupon_id": coupon_id,
            "account_id": account_id,
            "text_body": text_body,
            "bid_price": float(bid_price),
            "image_url": coupon.get("image_url", ""),
            "timestamp": int(time.time())
        }
        
        storage.save_coupon(coupon_id, coupon_data)
        coupon_ids.append(coupon_id)
    
    if not coupon_ids:
        return {"error": "No valid coupons to create"}
    
    return {
        "status": "Coupons published successfully",
        "coupon_ids": coupon_ids
    }

def get_coupons(req):
    """Retrieve and rank coupons based on context."""
    if not auth_req(req):
        return {"error": "Authentication failed"}
    
    context = req.get('context', '')
    n_coupons = req.get('N_COUPONS', config.DEFAULT_N_COUPONS)
    get_images = req.get('GET_IMAGES', False)
    
    if not context:
        return {"error": "Context is required"}
    
    if len(context) > config.MAX_CONTEXT_LENGTH:
        context = context[:config.MAX_CONTEXT_LENGTH]
    
    n_coupons = max(1, min(int(n_coupons), config.MAX_N_COUPONS))
    
    try:
        all_coupons = storage.get_all_coupons()
    except Exception as e:
        return {"error": f"Storage error: {str(e)}"}
    
    if not all_coupons:
        return {"coupons": []}
    
    # Score and rank coupons
    scored_coupons = []
    for coupon in all_coupons:
        score = score_coupon(context, coupon['text_body'])
        coupon_result = {
            "coupon_id": coupon['coupon_id'],
            "text": coupon['text_body'],
            "score": score,
            "bid_price": coupon['bid_price']
        }
        
        if get_images and coupon.get('image_url'):
            coupon_result['image_url'] = coupon['image_url']
        
        scored_coupons.append(coupon_result)
    
    sorted_coupons = sorted(
        scored_coupons, 
        key=lambda x: (x['score'], x['bid_price']), 
        reverse=True
    )
    
    return {"coupons": sorted_coupons[:n_coupons]}

def score_coupon(context, coupon_text):
    """Score a coupon's relevance to the given context using LLM."""
    prompt = f"""Rate the relevance of this coupon to the user's context on a scale from 0 to 1.
Return only a number between 0 and 1.

User Context: {context}
Coupon: {coupon_text}

Score:"""
    
    try:
        response = generate_completion(prompt)
        score = float(response.strip())
        return max(0.0, min(1.0, score))
    except (ValueError, AttributeError):
        return 0.5

@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": int(time.time())}), 200

if __name__ == "__main__":
    app.run(debug=config.DEBUG_MODE, host=config.SERVER_HOST, port=config.SERVER_PORT)