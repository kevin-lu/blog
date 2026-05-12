#!/bin/bash
# Test upload QR code

# Get token
TOKEN=$(curl -s -X POST http://127.0.0.1:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin2","password":"Admin@123456"}' \
  | grep -o '"access_token": "[^"]*"' \
  | cut -d'"' -f4)

echo "Token: ${TOKEN:0:50}..."

# Create a test image file
TEST_FILE="/tmp/test_qr.png"
echo "Creating test image..."
# Create a simple PNG file (1x1 pixel)
printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82' > "$TEST_FILE"

echo "Testing upload..."
curl -X POST http://127.0.0.1:5001/api/v1/donations/upload-qr \
  -H "Authorization: Bearer $TOKEN" \
  -F "type=wechat" \
  -F "file=@$TEST_FILE" \
  -v 2>&1

# Clean up
rm -f "$TEST_FILE"
