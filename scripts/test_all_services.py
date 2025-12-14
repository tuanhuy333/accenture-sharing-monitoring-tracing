#!/usr/bin/env python3
"""
Script tạo request đi qua tất cả 8 services để tạo traces và metrics
Returns trace IDs để xem trong Grafana
"""

import requests
import json
import sys
import urllib.parse
import time
from datetime import datetime

# URLs
SERVICES = {
    'user-service': 'http://localhost:8000',
    'order-service': 'http://localhost:8001',
    'payment-service': 'http://localhost:8002',
    'inventory-service': 'http://localhost:8003',
    'shipping-service': 'http://localhost:8004',
    'notification-service': 'http://localhost:8005',
    'review-service': 'http://localhost:8006',
    'auth-service': 'http://localhost:8007',
}

GRAFANA_URL = "http://localhost:3000"

def make_request_to_service(service_name, endpoint, method='GET', json_data=None):
    """Gửi request đến một service cụ thể"""
    url = f"{SERVICES[service_name]}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10, headers={"Content-Type": "application/json"})
        elif method == 'POST':
            response = requests.post(url, json=json_data, timeout=10, headers={"Content-Type": "application/json"})
        else:
            return None, None
        
        trace_id = None
        if response.status_code in [200, 201, 500]:
            try:
                data = response.json()
                trace_id = data.get('trace_id') or data.get('order', {}).get('trace_id') or data.get('payment_trace_id')
            except:
                pass
        
        return response, trace_id
    except requests.exceptions.RequestException as e:
        print(f"      ❌ Error: {e}")
        return None, None

def test_all_services():
    """
    Tạo requests đi qua tất cả 8 services
    """
    print("="*80)
    print("  🚀 TESTING ALL 8 SERVICES")
    print("="*80)
    print(f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    trace_ids = {}
    
    # Test từng service
    print("\n" + "-"*80)
    print("  📋 TESTING EACH SERVICE")
    print("-"*80)
    
    # 1. User Service
    print("\n  1️⃣  User Service")
    print("     GET /users")
    response, trace_id = make_request_to_service('user-service', '/users', 'GET')
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['user-service'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    time.sleep(0.5)
    
    # 2. Auth Service
    print("\n  2️⃣  Auth Service")
    print("     GET /health")
    response, trace_id = make_request_to_service('auth-service', '/health', 'GET')
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['auth-service'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    time.sleep(0.5)
    
    # 3. Order Service
    print("\n  3️⃣  Order Service")
    print("     GET /orders")
    response, trace_id = make_request_to_service('order-service', '/orders', 'GET')
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['order-service'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    time.sleep(0.5)
    
    # 4. Inventory Service
    print("\n  4️⃣  Inventory Service")
    print("     GET /inventory/1")
    response, trace_id = make_request_to_service('inventory-service', '/inventory/1', 'GET')
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['inventory-service'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    time.sleep(0.5)
    
    # 5. Payment Service
    print("\n  5️⃣  Payment Service")
    print("     GET /payments")
    response, trace_id = make_request_to_service('payment-service', '/payments', 'GET')
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['payment-service'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    time.sleep(0.5)
    
    # 6. Shipping Service
    print("\n  6️⃣  Shipping Service")
    print("     GET /health")
    response, trace_id = make_request_to_service('shipping-service', '/health', 'GET')
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['shipping-service'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    time.sleep(0.5)
    
    # 7. Notification Service
    print("\n  7️⃣  Notification Service")
    print("     GET /health")
    response, trace_id = make_request_to_service('notification-service', '/health', 'GET')
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['notification-service'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    time.sleep(0.5)
    
    # 8. Review Service
    print("\n  8️⃣  Review Service")
    print("     GET /health")
    response, trace_id = make_request_to_service('review-service', '/health', 'GET')
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['review-service'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    
    # Test flow qua nhiều services
    print("\n" + "-"*80)
    print("  🔄 TESTING FLOW ACROSS MULTIPLE SERVICES")
    print("-"*80)
    
    print("\n  📦 Creating order (Order → Inventory → Payment)")
    response, trace_id = make_request_to_service(
        'order-service', 
        '/orders', 
        'POST',
        {
            "user_id": 1,
            "total": 99.99,
            "inject_error": False
        }
    )
    if response:
        print(f"     Status: {response.status_code}")
        if trace_id:
            trace_ids['order-flow'] = trace_id
            print(f"     ✅ Trace ID: {trace_id}")
    
    # Summary
    print("\n" + "="*80)
    print("  📊 SUMMARY")
    print("="*80)
    
    if trace_ids:
        print(f"\n  ✅ Collected {len(trace_ids)} trace(s):")
        for service, tid in trace_ids.items():
            print(f"     - {service}: {tid}")
        
        # Create Grafana links
        print("\n  📊 View traces in Grafana:")
        for service, tid in trace_ids.items():
            grafana_link = create_grafana_trace_link(tid)
            if grafana_link:
                print(f"     {service}: {grafana_link}")
    else:
        print("\n  ⚠️  No trace IDs collected")
        print("     Make sure services are running and generating traces")
    
    return trace_ids

def create_grafana_trace_link(trace_id):
    """
    Creates Grafana Explore link with correct format to view specific trace
    Format: http://localhost:3000/explore?schemaVersion=1&panes={...}&orgId=1
    """
    if not trace_id or trace_id == 'N/A':
        return None
    
    # Create panes JSON with trace ID
    panes_data = {
        "54c": {
            "datasource": "tempo",
            "queries": [{
                "query": trace_id,
                "queryType": "traceql",
                "refId": "A",
                "datasource": {
                    "type": "tempo",
                    "uid": "tempo"
                },
                "limit": 20,
                "tableType": "traces"
            }],
            "range": {
                "from": "now-1h",
                "to": "now"
            }
        }
    }
    
    # Encode JSON to URL
    panes_json = json.dumps(panes_data)
    panes_encoded = urllib.parse.quote(panes_json)
    
    # Create full URL
    grafana_url = f"{GRAFANA_URL}/explore?schemaVersion=1&panes={panes_encoded}&orgId=1"
    
    return grafana_url

def main():
    """Main function"""
    trace_ids = test_all_services()
    
    if trace_ids:
        print("\n✅ Test completed successfully!")
        return trace_ids
    else:
        print("\n⚠️  Test completed but no traces collected")
        print("   Make sure services are running: docker-compose up -d")
        return {}

if __name__ == "__main__":
    try:
        trace_ids = main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
