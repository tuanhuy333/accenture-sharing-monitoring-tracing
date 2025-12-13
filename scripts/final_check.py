#!/usr/bin/env python3
"""Kiểm tra cuối cùng sau khi alert đã firing"""

import requests
import json

PROMETHEUS_URL = 'http://localhost:9090'
ALERTMANAGER_URL = 'http://localhost:9093'

print("="*80)
print("🔍 KIỂM TRA CUỐI CÙNG")
print("="*80)

# Kiểm tra Prometheus alerts
print("\n1️⃣ Prometheus Alerts:")
try:
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/alerts", timeout=5)
    if response.status_code == 200:
        data = response.json()
        alerts = data.get('data', {}).get('alerts', [])
        
        firing = [a for a in alerts if a.get('state') == 'firing']
        pending = [a for a in alerts if a.get('state') == 'pending']
        
        print(f"   ✅ Firing: {len(firing)}")
        print(f"   ⏳ Pending: {len(pending)}")
        
        if firing:
            print("\n   🔴 Alerts đang FIRING:")
            for alert in firing:
                labels = alert.get('labels', {})
                annotations = alert.get('annotations', {})
                print(f"      - {labels.get('alertname')}")
                print(f"        Service: {labels.get('job')}")
                print(f"        Severity: {labels.get('severity')}")
                if annotations.get('summary'):
                    print(f"        Summary: {annotations['summary']}")
        elif pending:
            print("\n   ⏳ Alerts đang PENDING (sẽ firing sau khi đủ thời gian):")
            for alert in pending:
                labels = alert.get('labels', {})
                print(f"      - {labels.get('alertname')} ({labels.get('job')})")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Kiểm tra Alertmanager alerts
print("\n2️⃣ Alertmanager Alerts:")
try:
    response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
    if response.status_code == 200:
        alerts = response.json()
        active = [a for a in alerts if a.get('status', {}).get('state') == 'active']
        
        print(f"   ✅ Active: {len(active)}")
        
        if active:
            print("\n   🔴 Alerts đang ACTIVE (đã gửi email):")
            for alert in active:
                labels = alert.get('labels', {})
                print(f"      - {labels.get('alertname')}")
                print(f"        Service: {labels.get('job')}")
                print(f"        Severity: {labels.get('severity')}")
        else:
            print("   ⚪ Chưa có alerts active trong Alertmanager")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

print("\n" + "="*80)
print("📧 KIỂM TRA EMAIL:")
print("="*80)
print("Email nhận: tuanhuy030799@gmail.com")
print("Subject: '🚨 CRITICAL: OrderServiceDown'")
print("\n💡 Nếu không thấy email:")
print("   1. Kiểm tra SPAM/JUNK folder")
print("   2. Xem logs: docker-compose logs -f alertmanager")
print("   3. Kiểm tra App Password: 'tahb vewk mmwp hryy'")
print("="*80)


