"""
S3 Storage module for Beavis API.
Handles all data persistence using AWS S3.
"""

import json
import boto3
from typing import Dict, List, Optional
from botocore.exceptions import ClientError
import config

class S3Storage:
    """Manages all S3 storage operations for coupons and accounts."""
    
    def __init__(self):
        """Initialize S3 storage client using config."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION
        )
        self.bucket = config.S3_BUCKET_NAME
        self.prefix = config.S3_PREFIX
        self.coupons_prefix = f"{self.prefix}coupons/"
        self.accounts_prefix = f"{self.prefix}accounts/"
    
    def save_coupon(self, coupon_id: str, coupon_data: Dict) -> bool:
        """Save a coupon to S3."""
        try:
            key = f"{self.coupons_prefix}{coupon_id}.json"
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(coupon_data),
                ContentType='application/json'
            )
            return True
        except ClientError as e:
            print(f"Error saving coupon: {e}")
            return False
    
    def get_coupon(self, coupon_id: str) -> Optional[Dict]:
        """Retrieve a specific coupon from S3."""
        try:
            key = f"{self.coupons_prefix}{coupon_id}.json"
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            data = response['Body'].read().decode('utf-8')
            return json.loads(data)
        except ClientError:
            return None
    
    def get_all_coupons(self) -> List[Dict]:
        """Retrieve all coupons from S3."""
        coupons = []
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket, Prefix=self.coupons_prefix)
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    if obj['Key'].endswith('/'):
                        continue
                    
                    try:
                        response = self.s3_client.get_object(Bucket=self.bucket, Key=obj['Key'])
                        data = response['Body'].read().decode('utf-8')
                        coupons.append(json.loads(data))
                    except Exception as e:
                        print(f"Error reading {obj['Key']}: {e}")
                        continue
            
            return coupons
        except ClientError as e:
            print(f"Error listing coupons: {e}")
            return []
    
    def delete_coupon(self, coupon_id: str) -> bool:
        """Delete a coupon from S3."""
        try:
            key = f"{self.coupons_prefix}{coupon_id}.json"
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            print(f"Error deleting coupon: {e}")
            return False
    
    def save_account(self, account_id: str, account_data: Dict) -> bool:
        """Save an account to S3."""
        try:
            key = f"{self.accounts_prefix}{account_id}.json"
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(account_data),
                ContentType='application/json'
            )
            return True
        except ClientError as e:
            print(f"Error saving account: {e}")
            return False
    
    def get_account(self, account_id: str) -> Optional[Dict]:
        """Retrieve an account from S3."""
        try:
            key = f"{self.accounts_prefix}{account_id}.json"
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            data = response['Body'].read().decode('utf-8')
            return json.loads(data)
        except ClientError:
            return None