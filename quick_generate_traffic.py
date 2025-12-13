#!/usr/bin/env python3
"""
Script nhanh để generate traffic - không cần input
"""

import requests
import time
import random

SERVICES = {
    'order-service': 'http://localhost:8001',
    'user-service': 'http://localhost:8000',
    'payment-service': 'http://localhost:8002',
    'inventory-service': 'http://localhost:8003',
}

ENDPOINTS = [
    ('order-service', '/', 'GET'),
    ('order-service', '/health', 'GET'),
    ('order-service', '/orders', 'GET'),
    ('order-service', '/orders?user_id=1', 'GET'),
    ('order-service', '/orders/1', 'GET'),
    ('order-service', '/orders/2', 'GET'),
    ('user-service', '/', 'GET'),
    ('user-service', '/health', 'GET'),
    ('user-service', '/users', 'GET'),
    ('user-service', '/users/1', 'GET'),
    ('payment-service', '/', 'GET'),
    ('payment-service', '/health', 'GET'),
    ('payment-service', '/payments', 'GET'),
    ('inventory-service', '/', 'GET'),
    ('inventory-service', '/health', 'GET'),
    ('inventory-service', '/inventory/1', 'GET'),
]

def make_request(service_name, endpoint, method):
    url = f"{SERVICES[service_name]}{endpoint}"
    try:
        if method == 'GET':
            requests.get(url, timeout=3)
        elif method == 'POST':
            requests.post(url, json={"user_id": 1, "total": 99.99}, timeout=3)
        return True
    except:
        return False

print("🚀 Đang tạo traffic đến các services...")
print("   (Gửi 200 requests để tạo metrics)\n")

success = 0
for i in range(200):
    service_name, endpoint, method = random.choice(ENDPOINTS)
    if make_request(service_name, endpoint, method):
        success += 1
    if (i + 1) % 50 == 0:
        print(f"   Đã gửi {i+1} requests ({success} thành công)...")
    time.sleep(0.05)

print(f"\n✅ Hoàn thành! Đã gửi 200 requests ({success} thành công)")
print("\n⏳ Đợi 30 giây để Prometheus scrape metrics...")
print("   Sau đó kiểm tra tại: http://localhost:9090/graph?g0.expr=http_requests_total")
print("   Hoặc chạy: python test_alerts.py")


