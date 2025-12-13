#!/usr/bin/env python3
"""
Script để trigger kịch bản end-to-end (DEPRECATED - Use tests/test_real_flow.py instead):
1. Tạo request đi qua tất cả services
2. Inject error vào payment-service
3. Alert sẽ được gửi với trace ID
4. Click vào link trong email để xem trace trong Grafana

NOTE: Sử dụng tests/test_real_flow.py để có đầy đủ tính năng (trace, logs, dashboard)
"""

import requests
import json
import time
import uuid

ORDER_SERVICE_URL = "http://localhost:8001"
GRAFANA_URL = "http://localhost:3000"

def trigger_error_scenario():
    """Trigger end-to-end scenario với error injection"""
    
    print("="*80)
    print("🚀 TRIGGER ERROR SCENARIO")
    print("="*80)
    print("\nKịch bản:")
    print("1. Tạo order request")
    print("2. Order service gọi inventory service")
    print("3. Order service gọi payment service (ERROR sẽ được inject)")
    print("4. Alert sẽ được trigger")
    print("5. Email sẽ có link đến Grafana để xem trace")
    print()
    
    # Generate a request ID for tracking
    request_id = str(uuid.uuid4())[:8]
    
    print(f"📋 Request ID: {request_id}")
    print(f"🔗 View in Grafana: {GRAFANA_URL}/explore?orgId=1&left=%5B%22now-15m%22,%22now%22,%22Tempo%22%5D")
    print()
    
    # Create order với error injection
    print("📦 Creating order with error injection...")
    try:
        response = requests.post(
            f"{ORDER_SERVICE_URL}/orders",
            json={
                "user_id": 1,
                "total": 99.99,
                "inject_error": True  # Inject error vào payment service
            },
            timeout=15,
            headers={
                "Content-Type": "application/json",
                "X-Request-ID": request_id
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 500:
            data = response.json()
            trace_id = data.get('trace_id', 'N/A')
            
            print(f"   ✅ Error triggered successfully!")
            print(f"   Error: {data.get('error', 'Unknown error')}")
            print(f"   Trace ID: {trace_id}")
            
            if data.get('order'):
                order = data['order']
                print(f"\n   Order Details:")
                print(f"      Order ID: {order.get('id')}")
                print(f"      User ID: {order.get('user_id')}")
                print(f"      Total: ${order.get('total')}")
                print(f"      Status: {order.get('status')}")
                if order.get('payment_error'):
                    print(f"      Payment Error: {order['payment_error']}")
                if order.get('payment_trace_id'):
                    print(f"      Payment Trace ID: {order['payment_trace_id']}")
                    trace_id = order['payment_trace_id']
            
            print(f"\n   📧 Alert sẽ được gửi trong vài giây...")
            print(f"   📊 Xem trace tại Grafana:")
            grafana_url = f"{GRAFANA_URL}/explore?orgId=1&left=%5B%22now-15m%22,%22now%22,%22Tempo%22%5D"
            print(f"      {grafana_url}")
            if trace_id != 'N/A':
                print(f"\n   🔍 Search trace ID trong Grafana: {trace_id}")
                
        elif response.status_code == 201:
            data = response.json()
            trace_id = data.get('trace_id', 'N/A')
            print(f"   ⚠️  Order created successfully (no error)")
            print(f"   Trace ID: {trace_id}")
            print(f"   Note: Error was not injected. Try again.")
            
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        print(f"   Make sure services are running: docker-compose up -d")
    
    print("\n" + "="*80)
    print("📋 NEXT STEPS:")
    print("="*80)
    print("1. Đợi 10-20 giây để alert kích hoạt")
    print("2. Kiểm tra email: tuanhuy030799@gmail.com")
    print("3. Click vào link 'View Traces in Grafana' trong email")
    print("4. Hoặc mở Grafana và search traces trong 15 phút gần đây")
    print("="*80)

if __name__ == "__main__":
    try:
        trigger_error_scenario()
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy bỏ")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")

