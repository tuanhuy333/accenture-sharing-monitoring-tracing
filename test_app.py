#!/usr/bin/env python3
"""
Script to generate traffic to the demo app for testing monitoring and tracing
"""
import requests
import time
import random
import sys

BASE_URL = "http://localhost:8000"
ENDPOINTS = ["/", "/health", "/slow", "/error", "/random"]

def make_request(endpoint):
    """Make a request to an endpoint"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, timeout=10)
        print(f"✓ {endpoint} - Status: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"✗ {endpoint} - Error: {e}")
        return None

def generate_traffic(duration=60, interval=1):
    """Generate traffic for a specified duration"""
    print(f"Generating traffic to {BASE_URL} for {duration} seconds...")
    print("Press Ctrl+C to stop early\n")
    
    start_time = time.time()
    request_count = 0
    
    try:
        while time.time() - start_time < duration:
            # Randomly select an endpoint
            endpoint = random.choice(ENDPOINTS)
            make_request(endpoint)
            request_count += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    elapsed = time.time() - start_time
    print(f"\nCompleted: {request_count} requests in {elapsed:.2f} seconds")
    print(f"Average rate: {request_count/elapsed:.2f} req/s")

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    
    generate_traffic(duration=duration, interval=interval)

