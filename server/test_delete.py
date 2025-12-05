#!/usr/bin/env python3
"""
Test script to verify DELETE endpoint
"""
import requests

# Test the DELETE endpoint
repo_id = "1bc7fa71c814258e"
url = f"http://192.168.0.11:5000/api/repository/{repo_id}"

print(f"Testing DELETE endpoint: {url}")
print("-" * 60)

try:
    response = requests.delete(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
