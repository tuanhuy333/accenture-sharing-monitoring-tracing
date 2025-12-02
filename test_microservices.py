#!/usr/bin/env python3
"""
Script to generate traffic across multiple microservices for testing monitoring and tracing
"""
import requests
import time
import random
import sys

USER_SERVICE_URL = "http://localhost:8000"
ORDER_SERVICE_URL = "http://localhost:8001"
PAYMENT_SERVICE_URL = "http://localhost:8002"

def make_request(url, method="GET", data=None):
    """Make a request to an endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        print(f"✓ {method} {url} - Status: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"✗ {method} {url} - Error: {e}")
        return None

def generate_traffic(duration=60, interval=1):
    """Generate traffic across all microservices"""
    print(f"Generating traffic across microservices for {duration} seconds...")
    print("Press Ctrl+C to stop early\n")
    
    endpoints = [
        # User Service
        (USER_SERVICE_URL + "/", "GET", None),
        (USER_SERVICE_URL + "/health", "GET", None),
        (USER_SERVICE_URL + "/users", "GET", None),
        (USER_SERVICE_URL + "/users/1", "GET", None),
        (USER_SERVICE_URL + "/users/2", "GET", None),
        (USER_SERVICE_URL + "/users/1/orders", "GET", None),
        
        # Order Service
        (ORDER_SERVICE_URL + "/", "GET", None),
        (ORDER_SERVICE_URL + "/health", "GET", None),
        (ORDER_SERVICE_URL + "/orders", "GET", None),
        (ORDER_SERVICE_URL + "/orders?user_id=1", "GET", None),
        (ORDER_SERVICE_URL + "/orders/1", "GET", None),
        (ORDER_SERVICE_URL + "/orders/2", "GET", None),
        (ORDER_SERVICE_URL + "/orders", "POST", {"user_id": 1, "total": 99.99}),
        
        # Payment Service
        (PAYMENT_SERVICE_URL + "/", "GET", None),
        (PAYMENT_SERVICE_URL + "/health", "GET", None),
        (PAYMENT_SERVICE_URL + "/payments", "GET", None),
        (PAYMENT_SERVICE_URL + "/payments?order_id=1", "GET", None),
        (PAYMENT_SERVICE_URL + "/payments/1", "GET", None),
        (PAYMENT_SERVICE_URL + "/payments", "POST", {"order_id": 1, "amount": 99.99}),
    ]
    
    start_time = time.time()
    request_count = 0
    
    try:
        while time.time() - start_time < duration:
            # Randomly select an endpoint
            url, method, data = random.choice(endpoints)
            make_request(url, method, data)
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

