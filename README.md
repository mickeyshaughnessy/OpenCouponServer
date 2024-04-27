# OpenCouponServer
This is an open API for coupon advertisers to upload and LLM chatbot providers to offer legit coupons.

There are two routes, one for businesses to upload coupons, one for chatbots to get coupons.

### GET_COUPONS
* Input: You can POST any text string up to 2k characters.
* Response:
  * A JSON body with "coupons" top level key and value a list of short (<256 character) coupon string, image URL pairs.
