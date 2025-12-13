#!/usr/bin/env python3
"""
Script creates a request that goes through multiple services but fails somewhere in the middle
Returns trace ID to view the trace in Grafana
"""

import requests
import json
import sys
import urllib.parse
from datetime import datetime

# URLs
ORDER_SERVICE_URL = "http://localhost:8001"
GRAFANA_URL = "http://localhost:3000"

def make_failed_request():
    """
    Creates a request that goes through multiple services:
    Order Service → Inventory Service → Payment Service (FAILS HERE)
    """
    print("="*80)
    print("  🚀 CREATING REQUEST ACROSS MULTIPLE SERVICES")
    print("="*80)
    print(f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Part 1: Simulated Flow
    print("\n" + "-"*80)
    print("  1️⃣  SIMULATED FLOW")
    print("-"*80)
    print("   Order Service → Inventory Service → Payment Service ❌ FAILS")
    
    # Part 2: Send and Response
    print("\n" + "-"*80)
    print("  2️⃣  SEND AND RESPONSE")
    print("-"*80)
    print("   Sending request...")
    
    try:
        response = requests.post(
            f"{ORDER_SERVICE_URL}/orders",
            json={
                "user_id": 1,
                "total": 99.99,
                "inject_error": True  # Inject error into payment service
            },
            timeout=15,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 500:
            data = response.json()
            trace_id = data.get('trace_id', 'N/A')
            
            # trace_id might be in the order object
            if data.get('order') and data['order'].get('payment_trace_id'):
                trace_id = data['order']['payment_trace_id']
            
            print(f"   ✅ Request failed at Payment Service!")
            print(f"   Error: {data.get('error', 'Unknown error')}")
            
            if data.get('order'):
                order = data['order']
                print(f"\n   📦 Order Details:")
                print(f"      Order ID: {order.get('id')}")
                print(f"      User ID: {order.get('user_id')}")
                print(f"      Total: ${order.get('total')}")
                print(f"      Status: {order.get('status')}")
                if order.get('payment_error'):
                    print(f"      Payment Error: {order['payment_error']}")
            
            # Part 3: Trace
            print("\n" + "-"*80)
            print("  3️⃣  TRACE")
            print("-"*80)
            print(f"   🔍 Trace ID: {trace_id}")
            
            # Create Grafana link with correct format
            grafana_link = create_grafana_trace_link(trace_id)
            if grafana_link:
                print(f"\n   📊 View trace in Grafana:")
                print(f"      {grafana_link}")
            
            return trace_id
            
        elif response.status_code == 201:
            data = response.json()
            trace_id = data.get('trace_id', 'N/A')
            print(f"   ⚠️  Request succeeded (no error)")
            print(f"   Note: Error was not injected. Check services.")
            
            # Part 3: Trace
            print("\n" + "-"*80)
            print("  3️⃣  TRACE")
            print("-"*80)
            print(f"   🔍 Trace ID: {trace_id}")
            
            # Create Grafana link
            grafana_link = create_grafana_trace_link(trace_id)
            if grafana_link:
                print(f"\n   📊 View trace in Grafana:")
                print(f"      {grafana_link}")
            
            return trace_id
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        print(f"   Make sure services are running: docker-compose up -d")
        return None

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
    trace_id = make_failed_request()
    
    if trace_id:
        return trace_id
    else:
        print("\n❌ Could not retrieve trace ID")
        sys.exit(1)

if __name__ == "__main__":
    try:
        trace_id = main()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

