# 🎟️ Beavis Open Coupon Server

An open-source API platform connecting coupon advertisers with LLM chatbot providers. Businesses upload coupons, AI chatbots retrieve contextually relevant offers. All data stored in S3 at `s3://mithrilmedia/OpenCouponServer/`.

## Features

- **RESTful API** for coupon management and retrieval
- **LLM-powered relevance scoring** using Ollama or OpenAI
- **S3-based storage** for scalable, persistent data
- **Flexible authentication** for advertisers and chatbots
- **Bid-based ranking** system for coupon visibility

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Advertisers │────────▶│  Beavis API  │◀────────│  Chatbots   │
└─────────────┘         └──────────────┘         └─────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   AWS S3    │
                        │ mithrilmedia│
                        └─────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  LLM (Ollama│
                        │  or OpenAI) │
                        └─────────────┘
```

## Storage Structure

All data is stored in S3 at `s3://mithrilmedia/OpenCouponServer/`:

```
OpenCouponServer/
├── coupons/
│   ├── {coupon_id_1}.json
│   ├── {coupon_id_2}.json
│   └── ...
└── accounts/
    ├── {account_id_1}.json
    ├── {account_id_2}.json
    └── ...
```

## Quick Start

### Prerequisites

- Python 3.8+
- AWS credentials with S3 access
- Ollama (optional, for local LLM) or OpenAI API key

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/beavis-api.git
cd beavis-api
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure AWS credentials:**
```bash
# Option 1: Use AWS CLI
aws configure

# Option 2: Set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

4. **Configure environment (optional):**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the server:**
```bash
python api_server.py
```

The API will be available at `http://localhost:8050`

## API Endpoints

### 1. `POST /MAKE_COUPONS` - Upload Coupons

**For advertisers to create coupons**

```json
{
  "account_id": "advertiser_123",
  "key": "your_api_key",
  "coupons": [
    {
      "text_body": "50% off electronics - valid until 12/31/2025",
      "bid_price": 0.75,
      "image_url": "https://example.com/coupon.jpg"
    }
  ]
}
```

**Response:**
```json
{
  "status": "Coupons published successfully",
  "coupon_ids": ["uuid-1", "uuid-2"]
}
```

### 2. `POST /GET_COUPONS` - Retrieve Coupons

**For chatbots to get relevant coupons**

```json
{
  "chatbot_id": "chatbot_456",
  "token": "your_token",
  "context": "User looking for laptop deals",
  "N_COUPONS": 5,
  "GET_IMAGES": true
}
```

**Response:**
```json
{
  "coupons": [
    {
      "coupon_id": "uuid-1",
      "text": "50% off electronics",
      "score": 0.92,
      "bid_price": 0.75,
      "image_url": "https://example.com/coupon.jpg"
    }
  ]
}
```

### 3. `GET /health` - Health Check

```json
{
  "status": "healthy",
  "timestamp": 1696089600
}
```

## Configuration

### Environment Variables

Create a `.env` file:

```env
# S3 Configuration
S3_BUCKET_NAME=mithrilmedia
S3_PREFIX=OpenCouponServer/
AWS_REGION=us-east-1

# AWS Credentials (or use AWS CLI configuration)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8050
DEBUG_MODE=True

# LLM Provider
LLM_PROVIDER=ollama  # or 'openai'

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

## Testing

### Run Integration Tests

```bash
python test_integration.py
```

### Create Test Accounts

```python
from utils import create_test_account

# Create advertiser account
create_test_account("advertiser_123", "test_key", "advertiser")

# Create chatbot account
create_test_account("chatbot_456", "test_token", "chatbot")
```

### Manual Testing

```bash
# Upload a coupon
curl -X POST http://localhost:8050/MAKE_COUPONS \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "advertiser_123",
    "key": "test_key",
    "coupons": [{
      "text_body": "Test coupon",
      "bid_price": 0.5
    }]
  }'

# Get coupons
curl -X POST http://localhost:8050/GET_COUPONS \
  -H "Content-Type: application/json" \
  -d '{
    "chatbot_id": "chatbot_456",
    "token": "test_token",
    "context": "Looking for deals",
    "N_COUPONS": 3
  }'
```

## Project Structure

```
beavis-api/
├── api_server.py          # Main Flask application
├── s3_storage.py          # S3 storage operations
├── utils.py               # Authentication and helpers
├── llm.py                 # LLM integration for scoring
├── config.py              # Configuration settings
├── test_integration.py    # Integration tests
├── requirements.txt       # Python dependencies
├── api_docs.html         # API documentation
└── README.md             # This file
```

## How It Works

1. **Advertisers** upload coupons with descriptions and bid prices to S3
2. **S3** stores all coupon and account data persistently
3. **Chatbots** send user context to retrieve relevant coupons
4. **LLM** scores each coupon's relevance (0-1 scale)
5. **API** ranks coupons by score and bid price
6. **Top coupons** are returned to the chatbot

## LLM Scoring

Coupons are scored using an LLM that evaluates relevance to the user's context:

- **Score range:** 0.0 to 1.0
- **Ranking:** Sorted by score (primary) and bid_price (secondary)
- **Providers:** Supports Ollama (local) or OpenAI (API)

## S3 Data Format

### Coupon Object
```json
{
  "coupon_id": "uuid-string",
  "account_id": "advertiser_123",
  "text_body": "50% off electronics",
  "bid_price": 0.75,
  "image_url": "https://example.com/image.jpg",
  "timestamp": 1696089600
}
```

### Account Object
```json
{
  "account_id": "account_123",
  "type": "advertiser",
  "pkey": "api_key_here"
}
```

## AWS Permissions

The application requires the following S3 permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::mithrilmedia/OpenCouponServer/*",
        "arn:aws:s3:::mithrilmedia"
      ]
    }
  ]
}
```

## Security Considerations

- All requests require authentication
- API keys stored securely in S3
- Rate limiting recommended for production
- HTTPS required for production deployment
- Use IAM roles instead of access keys when possible

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8050", "api_server:app"]
```

### Environment Setup

1. Set `DEBUG_MODE=False`
2. Configure production AWS credentials (use IAM roles)
3. Set up HTTPS/TLS
4. Implement rate limiting
5. Add logging and monitoring

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- **Documentation:** See `api_docs.html`
- **Issues:** GitHub Issues
- **Email:** api@beavis.com

## Roadmap

- [ ] Rate limiting implementation
- [ ] Webhook support for coupon expiration
- [ ] Advanced analytics dashboard
- [ ] Multi-language coupon support
- [ ] Geolocation-based filtering
- [ ] A/B testing framework
- [ ] S3 caching layer for performance

---

Built with ❤️ for the open-source community