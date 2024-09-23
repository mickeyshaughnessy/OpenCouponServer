import json, redis, uuid, time
from flask import Flask, jsonify, request
from utils import auth_req
from llm import generate_completion

redis_client = redis.StrictRedis()
app = Flask(__name__)

@app.route("/GET_COUPONS", methods=['POST'])
def get_coupons_route():
    req = request.get_json()
    return jsonify(get_coupons(req))

@app.route("/MAKE_COUPONS", methods=['POST'])
def make_coupons_route():
    req = request.get_json()
    return jsonify(make_coupons(req))

def make_coupons(req):
    if not auth_req(req): return {"error": "Authentication failed"}
    account_id, coupons = req.get("account_id"), req.get("coupons", [])
    if not coupons: return {"error": "No coupons provided"}
    coupon_ids = []
    for coupon in coupons:
        coupon_id = str(uuid.uuid4())
        coupon_data = {
            "coupon_id": coupon_id,
            "account_id": account_id,
            "text_body": coupon.get("text_body"),
            "bid_price": coupon.get("bid_price"),
            "timestamp": int(time.time())
        }
        redis_client.hset("coupons", coupon_id, json.dumps(coupon_data))
        coupon_ids.append(coupon_id)
    return {"status": "Coupons published successfully", "coupon_ids": coupon_ids}

def get_coupons(req):
    if not auth_req(req): return {"error": "Authentication failed"}
    context, n_coupons = req.get('context', ''), req.get('N_COUPONS', 5)
    all_coupons = [json.loads(coupon) for coupon in redis_client.hvals("coupons")]
    scored_coupons = [
        {**coupon, 'score': score_coupon(context, coupon['text_body'])}
        for coupon in all_coupons
    ]
    sorted_coupons = sorted(scored_coupons, key=lambda x: (x['score'], x['bid_price']), reverse=True)
    return {"coupons": sorted_coupons[:n_coupons]}

def score_coupon(context, coupon_text):
    prompt = f"""
    Rate the relevance of the following coupon to the user's context on a scale from 0 to 1.
    User Context: {context}
    Coupon Text: {coupon_text}
    Provide only the numerical score.
    """
    try:
        return float(generate_completion(prompt, api="ollama").strip())
    except ValueError:
        return 0.0

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)