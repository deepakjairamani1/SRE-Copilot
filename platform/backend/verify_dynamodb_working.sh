#!/bin/bash
echo "=========================================="
echo "DynamoDB Investigation Tracking - VERIFICATION"
echo "=========================================="

echo -e "\n1. Current DynamoDB state:"
docker exec sre-copilot-api python /app/check_dynamodb.py | grep -A 5 "core-athenamind"

echo -e "\n2. Triggering new investigation..."
curl -s -X POST http://localhost:7474/api/rca/investigate \
  -H "Content-Type: application/json" \
  -d '{"service": "core-athenamind"}' > /dev/null &

sleep 8

echo -e "\n3. Checking logs for custom start_time usage:"
docker logs --tail 50 sre-copilot-api 2>&1 | grep "✓ Using custom start_time" | tail -3

echo -e "\n4. Updated DynamoDB state:"
docker exec sre-copilot-api python /app/check_dynamodb.py | grep -A 5 "core-athenamind"

echo -e "\n=========================================="
echo "✓ VERIFICATION COMPLETE"
echo "=========================================="
echo ""
echo "If you see '✓ Using custom start_time' in logs,"
echo "then DynamoDB tracking is WORKING correctly!"
echo ""
