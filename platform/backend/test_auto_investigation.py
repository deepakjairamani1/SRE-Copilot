#!/usr/bin/env python3
"""Test script for auto-investigation system"""

import asyncio
import httpx
import json


BASE_URL = "http://localhost:8000"


async def test_start_auto_investigation():
    """Test starting auto-investigation"""
    print("🚀 Starting auto-investigation...")
    
    config = {
        "enabled": True,
        "slack_webhook_url": "",  # Add your webhook URL here
        "check_interval": 30,
        "cpu_threshold": 90.0,
        "ram_threshold": 90.0,
        "consecutive_errors_threshold": 3
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auto-investigation/start",
            json=config,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


async def test_status():
    """Test getting status"""
    print("\n📊 Checking status...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/auto-investigation/status",
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


async def test_trigger():
    """Test trigger evaluation"""
    print("\n🔍 Testing trigger evaluation...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auto-investigation/test-trigger",
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


async def test_stop():
    """Test stopping auto-investigation"""
    print("\n🛑 Stopping auto-investigation...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/auto-investigation/stop",
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))


async def main():
    """Run all tests"""
    try:
        await test_start_auto_investigation()
        await asyncio.sleep(2)
        await test_status()
        await asyncio.sleep(2)
        await test_trigger()
        await asyncio.sleep(2)
        # Uncomment to stop:
        # await test_stop()
        
        print("\n✅ All tests completed!")
        print("\nAuto-investigation is now running. Monitor with:")
        print(f"  watch -n 5 'curl -s {BASE_URL}/api/auto-investigation/status | jq'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
