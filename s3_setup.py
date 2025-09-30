"""
Setup script to initialize S3 bucket structure and create test accounts.
Run this once to set up your Beavis API environment.
"""

import boto3
from botocore.exceptions import ClientError
from s3_storage import S3Storage
from utils import create_test_account
import config

def check_s3_access():
    """Verify S3 bucket exists and is accessible."""
    print("Checking S3 access...")
    s3_client = boto3.client('s3')
    
    try:
        s3_client.head_bucket(Bucket=config.S3_BUCKET_NAME)
        print(f"✓ Connected to bucket: {config.S3_BUCKET_NAME}\n")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"✗ Bucket '{config.S3_BUCKET_NAME}' does not exist")
        elif error_code == '403':
            print(f"✗ Access denied to bucket '{config.S3_BUCKET_NAME}'")
        else:
            print(f"✗ Error: {e}")
        return False

def initialize_s3_structure():
    """Create the folder structure in S3."""
    print("Initializing S3 structure...")
    s3_client = boto3.client('s3')
    
    folders = [
        f"{config.S3_PREFIX}coupons/",
        f"{config.S3_PREFIX}accounts/"
    ]
    
    for folder in folders:
        try:
            s3_client.put_object(Bucket=config.S3_BUCKET_NAME, Key=folder, Body=b'')
            print(f"✓ Created: {folder}")
        except ClientError as e:
            print(f"✗ Failed: {folder}")
            return False
    
    print()
    return True

def create_demo_accounts():
    """Create demo accounts for testing."""
    print("Creating demo accounts...")
    
    accounts = [
        ("demo_advertiser", "demo_advertiser_key_123", "advertiser"),
        ("demo_chatbot", "demo_chatbot_token_456", "chatbot")
    ]
    
    for account_id, key, account_type in accounts:
        if create_test_account(account_id, key, account_type):
            print(f"✓ {account_type}: {account_id}")
        else:
            print(f"✗ Failed: {account_id}")
    
    print()
    return True

def create_demo_coupons():
    """Create demo coupons for testing."""
    print("Creating demo coupons...")
    
    storage = S3Storage(bucket_name=config.S3_BUCKET_NAME, prefix=config.S3_PREFIX)
    
    import time
    demo_coupons = [
        ("demo-coupon-1", "50% off all electronics - limited time!", 0.75),
        ("demo-coupon-2", "Free shipping on orders over $50", 0.40),
        ("demo-coupon-3", "Buy 2 get 1 free on all books", 0.60)
    ]
    
    for coupon_id, text, bid_price in demo_coupons:
        coupon_data = {
            "coupon_id": coupon_id,
            "account_id": "demo_advertiser",
            "text_body": text,
            "bid_price": bid_price,
            "image_url": "",
            "timestamp": int(time.time())
        }
        if storage.save_coupon(coupon_id, coupon_data):
            print(f"✓ {text[:40]}...")
        else:
            print(f"✗ Failed: {coupon_id}")
    
    print()
    return True

def main():
    """Run the complete setup process."""
    print("="*60)
    print("BEAVIS API S3 SETUP")
    print("="*60 + "\n")
    
    if not check_s3_access():
        print("\nConfigure AWS credentials: aws configure")
        return False
    
    if not initialize_s3_structure():
        return False
    
    if not create_demo_accounts():
        return False
    
    if not create_demo_coupons():
        return False
    
    print("="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nStart server: python api_server.py")
    print("\nDemo Credentials:")
    print("  Advertiser: demo_advertiser / demo_advertiser_key_123")
    print("  Chatbot: demo_chatbot / demo_chatbot_token_456")
    print(f"\nS3: s3://{config.S3_BUCKET_NAME}/{config.S3_PREFIX}")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted")
        exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        exit(1)