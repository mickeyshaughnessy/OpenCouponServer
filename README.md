# Beavis
Beavis, an open API for coupon advertisers to upload, and LLM chatbot providers to offer: 

#### coupons legit!!!

![image](https://github.com/user-attachments/assets/7d261204-199d-404d-8808-64ea230cef2a)

There are two routes: one for businesses to upload coupons they one to offer to potential customers and another one for chatbots to get coupons to offer to conversations.

----------------------------------------------------

### /GET_COUPONS(chatbot_id, context, N_COUPONS, GET_IMAGES): 

The route for LLM chatbot and other AI systems to get coupons.
*  HTTP POST JSON:
  * Requires valid (chatbot_id, token)
  * `context` : any ASCII text string up to 2k characters.
  * You can optionally pass a N_COUPONS value in the string. If you do, you assert you will offer N_COUPONS through the chatbot interface.
  * You can optionally pass a GET_IMAGES value. If you do, you assert you will display the images through the chatbot interface.

* Response:
  * A JSON body with `"coupons"` top level key: 
  * value a list of short (<256 character) coupon string, image URL pairs.

------------------------------------------------------------


### /MAKE_COUPONS(...):

The route for businesses to upload coupons. `bid_price` is the maximum amount the business agrees to pay when the coupon is redeemed. 
 
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

  ` response = {"message" : "success"}

