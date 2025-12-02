#!/usr/bin/env python3
"""
Script to generate traffic across all microservices for testing monitoring and tracing
"""
import requests
import time
import random
import sys

SERVICES = {
    "user-service": "http://localhost:8000",
    "order-service": "http://localhost:8001",
    "payment-service": "http://localhost:8002",
    "inventory-service": "http://localhost:8003",
    "shipping-service": "http://localhost:8004",
    "notification-service": "http://localhost:8005",
    "review-service": "http://localhost:8006",
    "auth-service": "http://localhost:8007",
}

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

def generate_traffic(duration=60, interval=0.5):
    """Generate traffic across all microservices"""
    print(f"Generating traffic across {len(SERVICES)} microservices for {duration} seconds...")
    print("Press Ctrl+C to stop early\n")
    
    endpoints = [
        # User Service
        (SERVICES["user-service"] + "/", "GET", None),
        (SERVICES["user-service"] + "/health", "GET", None),
        (SERVICES["user-service"] + "/users", "GET", None),
        (SERVICES["user-service"] + "/users/1", "GET", None),
        (SERVICES["user-service"] + "/users/2", "GET", None),
        (SERVICES["user-service"] + "/users/1/orders", "GET", None),
        
        # Order Service
        (SERVICES["order-service"] + "/", "GET", None),
        (SERVICES["order-service"] + "/health", "GET", None),
        (SERVICES["order-service"] + "/orders", "GET", None),
        (SERVICES["order-service"] + "/orders?user_id=1", "GET", None),
        (SERVICES["order-service"] + "/orders/1", "GET", None),
        (SERVICES["order-service"] + "/orders/2", "GET", None),
        (SERVICES["order-service"] + "/orders", "POST", {"user_id": 1, "total": 99.99}),
        
        # Payment Service
        (SERVICES["payment-service"] + "/", "GET", None),
        (SERVICES["payment-service"] + "/health", "GET", None),
        (SERVICES["payment-service"] + "/payments", "GET", None),
        (SERVICES["payment-service"] + "/payments?order_id=1", "GET", None),
        (SERVICES["payment-service"] + "/payments/1", "GET", None),
        (SERVICES["payment-service"] + "/payments", "POST", {"order_id": 1, "amount": 99.99}),
        
        # Inventory Service
        (SERVICES["inventory-service"] + "/", "GET", None),
        (SERVICES["inventory-service"] + "/health", "GET", None),
        (SERVICES["inventory-service"] + "/inventory", "GET", None),
        (SERVICES["inventory-service"] + "/inventory/1", "GET", None),
        (SERVICES["inventory-service"] + "/inventory/2", "GET", None),
        (SERVICES["inventory-service"] + "/inventory/1/reserve", "POST", {"quantity": 1}),
        
        # Shipping Service
        (SERVICES["shipping-service"] + "/", "GET", None),
        (SERVICES["shipping-service"] + "/health", "GET", None),
        (SERVICES["shipping-service"] + "/shipping/check", "GET", None),
        (SERVICES["shipping-service"] + "/shipping", "GET", None),
        (SERVICES["shipping-service"] + "/shipping/1", "GET", None),
        (SERVICES["shipping-service"] + "/shipping", "POST", {"order_id": 1}),
        
        # Notification Service
        (SERVICES["notification-service"] + "/", "GET", None),
        (SERVICES["notification-service"] + "/health", "GET", None),
        (SERVICES["notification-service"] + "/notifications", "GET", None),
        (SERVICES["notification-service"] + "/notifications", "POST", {"type": "order_confirmed"}),
        
        # Review Service
        (SERVICES["review-service"] + "/", "GET", None),
        (SERVICES["review-service"] + "/health", "GET", None),
        (SERVICES["review-service"] + "/reviews", "GET", None),
        (SERVICES["review-service"] + "/reviews?product_id=1", "GET", None),
        (SERVICES["review-service"] + "/reviews/1", "GET", None),
        (SERVICES["review-service"] + "/reviews", "POST", {"product_id": 1, "rating": 5, "comment": "Great!"}),
        
        # Auth Service
        (SERVICES["auth-service"] + "/", "GET", None),
        (SERVICES["auth-service"] + "/health", "GET", None),
        (SERVICES["auth-service"] + "/auth/login", "POST", {"username": "user1"}),
        (SERVICES["auth-service"] + "/auth/verify?token=token_12345", "GET", None),
        (SERVICES["auth-service"] + "/auth/users/1/permissions", "GET", None),
    ]
    
    start_time = time.time()
    request_count = 0
    
    try:
        while time.time() - start_time < duration:
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
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    
    generate_traffic(duration=duration, interval=interval)

