#!/usr/bin/env python3
"""Quick test to verify DynamoDB is working"""
import os
import sys
from datetime import datetime, timezone

# Add app to path
sys.path.insert(0, '/app')

from app.clients.dynamodb_client import DynamoDBClient

def test_dynamodb():
    print("=" * 60)
    print("Testing DynamoDB Connection")
    print("=" * 60)
    
    # Check environment
    enabled = os.getenv("DYNAMODB_ENABLED", "false").lower() == "true"
    region = os.getenv("DYNAMODB_REGION", "us-east-1")
    has_key = bool(os.getenv("AWS_ACCESS_KEY_ID"))
    has_secret = bool(os.getenv("AWS_SECRET_ACCESS_KEY"))
    
    print(f"\nEnvironment:")
    print(f"  DYNAMODB_ENABLED: {enabled}")
    print(f"  DYNAMODB_REGION: {region}")
    print(f"  AWS_ACCESS_KEY_ID: {'✓ Set' if has_key else '✗ Not set'}")
    print(f"  AWS_SECRET_ACCESS_KEY: {'✓ Set' if has_secret else '✗ Not set'}")
    
    # Initialize client
    print(f"\nInitializing DynamoDB client...")
    client = DynamoDBClient(enabled=enabled, region=region)
    
    if not client.enabled:
        print("✗ DynamoDB client is DISABLED")
        return False
    
    print("✓ DynamoDB client initialized")
    
    # Test operations
    test_service = "test-service-live"
    test_incident = "INC-TEST-LIVE-001"
    test_time = datetime.now(timezone.utc).isoformat()
    
    print(f"\nTest 1: Get last investigation time (should be None)")
    last_time = client.get_last_investigation_time(test_service)
    print(f"  Result: {last_time}")
    
    print(f"\nTest 2: Update investigation time")
    print(f"  Service: {test_service}")
    print(f"  Time: {test_time}")
    print(f"  Incident: {test_incident}")
    success = client.update_investigation_time(test_service, test_time, test_incident)
    print(f"  Result: {'✓ Success' if success else '✗ Failed'}")
    
    if success:
        print(f"\nTest 3: Get last investigation time (should return our time)")
        last_time = client.get_last_investigation_time(test_service)
        print(f"  Result: {last_time}")
        print(f"  Match: {'✓ Yes' if last_time == test_time else '✗ No'}")
        
        if last_time == test_time:
            print("\n" + "=" * 60)
            print("✓ DynamoDB is WORKING CORRECTLY!")
            print("=" * 60)
            return True
    
    print("\n" + "=" * 60)
    print("✗ DynamoDB test FAILED")
    print("=" * 60)
    return False

if __name__ == "__main__":
    try:
        success = test_dynamodb()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
