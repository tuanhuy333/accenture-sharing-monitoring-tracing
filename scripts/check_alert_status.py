#!/usr/bin/env python3
"""Kiểm tra trạng thái alert sau khi dừng service"""

import requests
import time

PROMETHEUS_URL = 'http://localhost:9090'
ALERTMANAGER_URL = 'http://localhost:9093'

print("⏳ Đợi 70 giây để alert kích hoạt...")
print("   (Alert rule: up{job=\"order-service\"} == 0 for 1m)")
print()

for i in range(14):
    time.sleep(5)
    print(f"   Đã đợi {(i+1)*5} giây...", end='\r')

print("\n\n📊 Kiểm tra alerts...\n")

# Kiểm tra Prometheus alerts
try:
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/alerts", timeout=5)
    if response.status_code == 200:
        data = response.json()
        alerts = data.get('data', {}).get('alerts', [])
        
        firing_alerts = [a for a in alerts if a.get('state') == 'firing']
        pending_alerts = [a for a in alerts if a.get('state') == 'pending']
        
        print(f"✅ Prometheus Alerts:")
        print(f"   - Firing: {len(firing_alerts)}")
        print(f"   - Pending: {len(pending_alerts)}")
        
        for alert in firing_alerts:
            labels = alert.get('labels', {})
            print(f"\n   🔴 FIRING: {labels.get('alertname')}")
            print(f"      Service: {labels.get('job')}")
            print(f"      Severity: {labels.get('severity')}")
except Exception as e:
    print(f"❌ Lỗi khi kiểm tra Prometheus: {e}")

# Kiểm tra Alertmanager alerts
try:
    response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
    if response.status_code == 200:
        alerts = response.json()
        active_alerts = [a for a in alerts if a.get('status', {}).get('state') == 'active']
        
        print(f"\n✅ Alertmanager Alerts:")
        print(f"   - Active: {len(active_alerts)}")
        
        for alert in active_alerts:
            labels = alert.get('labels', {})
            print(f"\n   🔴 ACTIVE: {labels.get('alertname')}")
            print(f"      Service: {labels.get('job')}")
            print(f"      Severity: {labels.get('severity')}")
except Exception as e:
    print(f"❌ Lỗi khi kiểm tra Alertmanager: {e}")

print("\n" + "="*80)
print("📧 KIỂM TRA EMAIL:")
print("="*80)
print("1. Kiểm tra hộp thư: tuanhuy030799@gmail.com")
print("2. Kiểm tra cả thư mục SPAM/JUNK")
print("3. Subject sẽ là: '🚨 CRITICAL: OrderServiceDown'")
print()
print("💡 Nếu không thấy email:")
print("   - Xem logs: docker-compose logs -f alertmanager")
print("   - Kiểm tra App Password đã đúng chưa")
print("="*80)


