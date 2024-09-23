# Beavis API Documentation

Beavis is an open API for coupon advertisers to upload, and for LLM chatbot providers to offer coupons.

![Beavis API Logo](https://github.com/user-attachments/assets/7d261204-199d-404d-8808-64ea230cef2a)

## API Routes

There are two main routes:

1. For chatbots to get coupons to offer in conversations
2. For businesses to upload coupons they want to offer to potential customers 

### 1. GET_COUPONS

This route is for LLM chatbots and other AI systems to retrieve coupons.

**Endpoint:** `/GET_COUPONS`

**Method:** POST

**Request Body (JSON):**
```json
{
  "chatbot_id": "string",
  "token": "string",
  "context": "string",
  "N_COUPONS": "number (optional)",
  "GET_IMAGES": "boolean (optional)"
}
```

- `chatbot_id` and `token`: Required for authentication
- `context`: Any ASCII text string up to 2000 characters
- `N_COUPONS`: Optional. If provided, you assert you will offer this many coupons through the chatbot interface
- `GET_IMAGES`: Optional. If true, you assert you will display the images through the chatbot interface

**Response:**

```json
{
  "coupons": [
    {
      "text": "string (max 256 characters)",
      "image_url": "string"
    }
  ]
}
```

### 2. MAKE_COUPONS

This route is for businesses to upload coupons.

**Endpoint:** `/MAKE_COUPONS`

**Method:** POST

**Request Body (JSON):**
```json
{
  "advertiser_key": "string",
  "advertiser_name": "string",
  "advertiser_location": "string",
  "coupon_text": "string",
  "coupon_image": "string (URL)",
  "bid_price": "string"
}
```

- `bid_price`: The maximum amount the business agrees to pay when the coupon is redeemed

**Example Request:**
```json
{
  "advertiser_key": "123456",
  "advertiser_name": "Nutella",
  "advertiser_location": "Seattle, WA",
  "coupon_text": "Here's 10% off a jar of Nutella!",
  "coupon_image": "www.s3.nutellacoupons/123",
  "bid_price": "$0.01 per coupon offer"
}
```

**Response:**
```json
{
  "message": "success"
}
```
