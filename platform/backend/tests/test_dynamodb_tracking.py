"""
Test DynamoDB investigation tracking
"""
import asyncio
import os
from datetime import datetime, timezone
from app.clients.dynamodb_client import DynamoDBClient


async def test_dynamodb_tracking():
    """Test DynamoDB tracking functionality"""
    
    # Test with disabled client
    print("=== Test 1: Disabled Client ===")
    client_disabled = DynamoDBClient(enabled=False)
    result = client_disabled.get_last_investigation_time("test-service")
    print(f"Disabled client result: {result}")
    assert result is None, "Disabled client should return None"
    print("✓ Disabled client test passed\n")
    
    # Test with enabled client (requires AWS credentials)
    print("=== Test 2: Enabled Client ===")
    dynamodb_enabled = os.getenv("DYNAMODB_ENABLED", "false").lower() == "true"
    
    if not dynamodb_enabled:
        print("⚠ DynamoDB not enabled in environment. Set DYNAMODB_ENABLED=true to test.")
        print("⚠ Also ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set.")
        return
    
    client = DynamoDBClient(enabled=True, region=os.getenv("DYNAMODB_REGION", "us-east-1"))
    
    if not client.enabled:
        print("✗ DynamoDB client failed to initialize (check AWS credentials)")
        return
    
    print("✓ DynamoDB client initialized successfully")
    
    # Test service
    test_service = "test-service-001"
    test_incident_id = "INC-TEST-001"
    test_timestamp = datetime.now(timezone.utc).isoformat()
    
    # Test 1: Get non-existent service
    print(f"\n--- Getting last investigation for new service: {test_service} ---")
    last_time = client.get_last_investigation_time(test_service)
    print(f"Result: {last_time}")
    assert last_time is None, "New service should have no previous investigation"
    print("✓ New service returns None")
    
    # Test 2: Update investigation time
    print(f"\n--- Updating investigation time ---")
    print(f"Service: {test_service}")
    print(f"Timestamp: {test_timestamp}")
    print(f"Incident ID: {test_incident_id}")
    success = client.update_investigation_time(test_service, test_timestamp, test_incident_id)
    print(f"Update result: {success}")
    assert success, "Update should succeed"
    print("✓ Update successful")
    
    # Test 3: Get updated time
    print(f"\n--- Getting last investigation after update ---")
    last_time = client.get_last_investigation_time(test_service)
    print(f"Result: {last_time}")
    assert last_time == test_timestamp, f"Should return {test_timestamp}"
    print("✓ Retrieved correct timestamp")
    
    # Test 4: Update again (simulate second investigation)
    print(f"\n--- Simulating second investigation ---")
    import time
    time.sleep(2)
    test_timestamp_2 = datetime.now(timezone.utc).isoformat()
    test_incident_id_2 = "INC-TEST-002"
    success = client.update_investigation_time(test_service, test_timestamp_2, test_incident_id_2)
    assert success, "Second update should succeed"
    
    last_time = client.get_last_investigation_time(test_service)
    print(f"New timestamp: {last_time}")
    assert last_time == test_timestamp_2, "Should return updated timestamp"
    print("✓ Second investigation tracked correctly")
    
    print("\n=== All Tests Passed! ===")
    print(f"\nDynamoDB table '{client.table_name}' is working correctly.")
    print("You can view it in AWS Console: https://console.aws.amazon.com/dynamodb/")


if __name__ == "__main__":
    asyncio.run(test_dynamodb_tracking())
