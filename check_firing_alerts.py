#!/usr/bin/env python3
"""Kiểm tra các alerts đang firing"""

import requests
import json

PROMETHEUS_URL = 'http://localhost:9090'
ALERTMANAGER_URL = 'http://localhost:9093'

print("="*80)
print("🔍 KIỂM TRA ALERTS ĐANG FIRING")
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
        inactive = [a for a in alerts if a.get('state') == 'inactive']
        
        print(f"   🔴 Firing: {len(firing)}")
        print(f"   ⏳ Pending: {len(pending)}")
        print(f"   ⚪ Inactive: {len(inactive)}")
        
        if firing:
            print("\n   🔴 ALERTS ĐANG FIRING:")
            print("-" * 80)
            for alert in firing:
                labels = alert.get('labels', {})
                annotations = alert.get('annotations', {})
                active_at = alert.get('activeAt', 'N/A')
                
                alertname = labels.get('alertname', 'Unknown')
                severity = labels.get('severity', 'unknown')
                job = labels.get('job', 'N/A')
                service = labels.get('service', 'N/A')
                
                severity_icon = "🚨" if severity == "critical" else "⚠️" if severity == "warning" else "ℹ️"
                
                print(f"\n   {severity_icon} {alertname}")
                print(f"      Severity: {severity}")
                print(f"      Job: {job}")
                if service != 'N/A':
                    print(f"      Service: {service}")
                if annotations.get('summary'):
                    print(f"      Summary: {annotations['summary']}")
                if annotations.get('description'):
                    print(f"      Description: {annotations['description']}")
                print(f"      Active since: {active_at}")
        else:
            print("\n   ✅ Không có alerts nào đang firing")
            
        if pending:
            print("\n   ⏳ ALERTS ĐANG PENDING:")
            for alert in pending[:5]:
                labels = alert.get('labels', {})
                print(f"      - {labels.get('alertname')} ({labels.get('job', 'N/A')})")
            if len(pending) > 5:
                print(f"      ... và {len(pending) - 5} alerts khác")
                
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Kiểm tra Alertmanager alerts
print("\n2️⃣ Alertmanager Alerts:")
try:
    response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
    if response.status_code == 200:
        alerts = response.json()
        active = [a for a in alerts if a.get('status', {}).get('state') == 'active']
        
        print(f"   🔴 Active: {len(active)}")
        
        if active:
            print("\n   🔴 ALERTS ACTIVE (đã gửi email):")
            print("-" * 80)
            for alert in active:
                labels = alert.get('labels', {})
                annotations = alert.get('annotations', {})
                starts_at = alert.get('startsAt', 'N/A')
                
                alertname = labels.get('alertname', 'Unknown')
                severity = labels.get('severity', 'unknown')
                job = labels.get('job', 'N/A')
                
                severity_icon = "🚨" if severity == "critical" else "⚠️" if severity == "warning" else "ℹ️"
                
                print(f"\n   {severity_icon} {alertname}")
                print(f"      Severity: {severity}")
                print(f"      Job: {job}")
                if annotations.get('summary'):
                    print(f"      Summary: {annotations['summary']}")
                print(f"      Started: {starts_at}")
        else:
            print("\n   ✅ Không có alerts nào active trong Alertmanager")
            
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

print("\n" + "="*80)
print("💡 LƯU Ý:")
print("="*80)
print("Nếu có quá nhiều alerts firing, có thể do:")
print("1. Thời gian alert quá ngắn (10s) - dễ trigger false positives")
print("2. Ngưỡng alert quá thấp")
print("3. Services thực sự có vấn đề")
print("\nĐể giảm false positives, có thể:")
print("- Tăng thời gian 'for' lên 30s hoặc 1m")
print("- Điều chỉnh ngưỡng trong alert rules")
print("- Kiểm tra metrics thực tế tại: http://localhost:9090/graph")
print("="*80)


