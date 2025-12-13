#!/usr/bin/env python3
"""Trigger multiple errors để đảm bảo alert được trigger"""

import requests
import time

ORDER_SERVICE_URL = "http://localhost:8001"

print("="*80)
print("🚀 TRIGGER MULTIPLE ERRORS ĐỂ TRIGGER ALERT")
print("="*80)
print("\nSẽ gửi 10 requests với error injection...")
print("Alert rule yêu cầu: error rate > 0.1 req/s\n")

trace_ids = []

for i in range(10):
    try:
        print(f"Request {i+1}/10...", end=" ")
        response = requests.post(
            f"{ORDER_SERVICE_URL}/orders",
            json={
                "user_id": 1,
                "total": 99.99,
                "inject_error": True
            },
            timeout=15
        )
        
        if response.status_code == 500:
            data = response.json()
            trace_id = data.get('trace_id', 'N/A')
            if trace_id != 'N/A':
                trace_ids.append(trace_id)
            print(f"✅ Error (Trace: {trace_id[:8]}...)")
        else:
            print(f"⚠️ Status: {response.status_code}")
        
        time.sleep(0.5)  # Đợi 0.5s giữa các requests
        
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n✅ Đã gửi 10 requests")
print(f"📋 Trace IDs: {len(trace_ids)}")
if trace_ids:
    print(f"   First trace: {trace_ids[0]}")
    print(f"   Last trace: {trace_ids[-1]}")

print("\n" + "="*80)
print("⏳ Đợi 15 giây để Prometheus tính toán error rate...")
print("="*80)

time.sleep(15)

print("\n📊 Kiểm tra alerts...")
try:
    import requests as req_check
    response = req_check.get("http://localhost:9090/api/v1/alerts", timeout=5)
    if response.status_code == 200:
        data = response.json()
        alerts = data.get('data', {}).get('alerts', [])
        firing = [a for a in alerts if a.get('state') == 'firing']
        
        if firing:
            print(f"✅ Có {len(firing)} alerts đang FIRING!")
            for alert in firing:
                labels = alert.get('labels', {})
                print(f"   🔴 {labels.get('alertname')} - {labels.get('service', 'N/A')}")
        else:
            print("⚠️ Chưa có alerts firing")
            print("   Kiểm tra tại: http://localhost:9090/alerts")
except:
    print("   Không thể kiểm tra alerts")

print("\n" + "="*80)
print("📧 KIỂM TRA EMAIL:")
print("="*80)
print("Email: tuanhuy030799@gmail.com")
print("Subject: 🚨 CRITICAL: HighErrorRate")
print("="*80)

