#!/usr/bin/env python3
"""Test upload with detailed logging"""
import requests

# Login to get token
login_response = requests.post(
    'http://127.0.0.1:5001/api/v1/auth/login',
    json={'username': 'admin2', 'password': 'Admin@123456'}
)
token = login_response.json()['access_token']
print(f"Token: {token[:50]}...")

# Create a test image
test_file = '/tmp/test_qr2.png'
with open(test_file, 'wb') as f:
    # Write a simple PNG
    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82')

# Test upload
headers = {
    'Authorization': f'Bearer {token}'
}

files = {
    'file': ('test_qr.png', open(test_file, 'rb'), 'image/png')
}
data = {
    'type': 'wechat'
}

print("\nSending upload request...")
response = requests.post(
    'http://127.0.0.1:5001/api/v1/donations/upload-qr',
    headers=headers,
    files=files,
    data=data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

import os
os.remove(test_file)
