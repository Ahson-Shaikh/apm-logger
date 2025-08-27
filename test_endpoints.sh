#!/bin/bash

# Test script for APM Logger endpoints
# Make sure the app is running first: uvicorn app:app --host 0.0.0.0 --port 8000

BASE_URL="http://localhost:8000"

echo "Testing APM Logger endpoints..."
echo "================================"

echo ""
echo "1. Health check (should return 200):"
curl -s "$BASE_URL/health" | jq '.' 2>/dev/null || curl -s "$BASE_URL/health"

echo ""
echo "2. Log error without exception (should return 200):"
curl -s "$BASE_URL/log-error?msg=Test%20error%20message" | jq '.' 2>/dev/null || curl -s "$BASE_URL/log-error?msg=Test%20error%20message"

echo ""
echo "3. Payment fail with structured logging (should return 200):"
curl -s "$BASE_URL/payment/fail?order_id=TEST-001&user_id=test-user" | jq '.' 2>/dev/null || curl -s "$BASE_URL/payment/fail?order_id=TEST-001&user_id=test-user"

echo ""
echo "4. Handled exception (should return 500):"
curl -s "$BASE_URL/zero" | jq '.' 2>/dev/null || curl -s "$BASE_URL/zero"

echo ""
echo "5. Unhandled exception (should return 500):"
curl -s "$BASE_URL/boom" | jq '.' 2>/dev/null || curl -s "$BASE_URL/boom"

echo ""
echo "================================"
echo "All endpoints tested!"
echo ""
echo "Note: Check your APM server for captured errors and logs."
echo "If APM server is not running, events will be queued until connection is established." 