# OpenCouponServer
This is an open API for coupon advertisers to upload and LLM chatbot providers to offer legit coupons.

There are two routes, one for businesses to upload coupons, one for chatbots to get coupons.

### GET_COUPONS
* Input: You can POST any text string up to 2k characters.
  * You can optionally pass a N_COUPONS value in the string. If you do, you assert you will offer N_COUPONS through the chatbot interface.
  * You can optionally pass a GET_IMAGES value. If you do, you assert you will display the images through the chatbot interface.

* Response:
  * A JSON body with "coupons" top level key and value a list of short (<256 character) coupon string, image URL pairs.

### MAKE_COUPONS
* Input: POST JSON containing:
  * advertiser_key
  * advertiser_name
  * advertiser_location
  * coupon_text
  * coupon_image
  * bid_price

  Eg:

  ` request = {
      "advertiser_key" : "123456",
      "advertiser_name" : "Nutella",
      "advertiser_location" : "Seattle, WA",
      "coupon_text" : "Here's 10% off a jar of Nutella!",
      "coupon_image" : "www.s3.nutellacoupons/123",
      "bid_price" : "$0.01 per coupon offer"
  }


