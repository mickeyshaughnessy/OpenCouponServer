
import json, redis, uuid, time
import config, handlers
from flask import Flask, jsonify, request
redis = redis.StrictRedis()

app = Flask(__name__)

## Routes ##
#  GET_COUPONS 
#  MAKE_COUPONS 

@app.route("/GET_COUPONS", methods=['POST'])
def get_coupons():
    req = request.get_json()
    resp = {}
    resp["coupons"] = handlers.get_coupons(req)
    return json.dumps(resp)

@app.route("/MAKE_COUPONS", methods=['POST'])
def make_coupons():
    req = request.get_json()
    resp = handlers.make_coupons(req)
    return json.dumps(resp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)
