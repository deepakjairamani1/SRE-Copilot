#!/usr/bin/env python3
"""Check what's stored in DynamoDB"""
import os
import sys
import boto3
from datetime import datetime

def check_dynamodb():
    print("=" * 70)
    print("DynamoDB Investigation Tracker - Current Data")
    print("=" * 70)
    
    # Get credentials
    region = os.getenv("DYNAMODB_REGION", "us-east-1")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if not access_key or not secret_key:
        print("✗ AWS credentials not found in environment")
        return
    
    print(f"\nRegion: {region}")
    print(f"Access Key: {access_key[:10]}...")
    
    # Connect to DynamoDB
    try:
        dynamodb = boto3.resource('dynamodb', region_name=region)
        table = dynamodb.Table('sre-investigation-tracker')
        
        print(f"\n✓ Connected to table: sre-investigation-tracker")
        
        # Scan all items
        response = table.scan()
        items = response.get('Items', [])
        
        print(f"\n📊 Total records: {len(items)}")
        print("=" * 70)
        
        if not items:
            print("\n⚠ No records found in DynamoDB table")
            print("\nThis means:")
            print("  - Either no investigations have been run yet")
            print("  - Or the DynamoDB integration is not working")
            return
        
        # Display each record
        for i, item in enumerate(items, 1):
            print(f"\n{i}. Service: {item.get('service', 'N/A')}")
            print(f"   Last Investigation: {item.get('last_investigation_time', 'N/A')}")
            print(f"   Last Incident ID: {item.get('last_incident_id', 'N/A')}")
            print(f"   Updated At: {item.get('updated_at', 'N/A')}")
            
            # Calculate time since last investigation
            if item.get('last_investigation_time'):
                try:
                    last_time = datetime.fromisoformat(item['last_investigation_time'].replace('Z', '+00:00'))
                    now = datetime.now(last_time.tzinfo)
                    diff = now - last_time
                    minutes = int(diff.total_seconds() / 60)
                    print(f"   Time Since: {minutes} minutes ago")
                except:
                    pass
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_dynamodb()
