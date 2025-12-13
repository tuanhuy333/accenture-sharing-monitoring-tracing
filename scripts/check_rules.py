#!/usr/bin/env python3
"""Kiểm tra alert rules đã được load chưa"""

import requests
import json

PROMETHEUS_URL = 'http://localhost:9090'

try:
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/rules", timeout=5)
    if response.status_code == 200:
        data = response.json()
        groups = data.get('data', {}).get('groups', [])
        
        print("="*80)
        print("📋 KIỂM TRA ALERT RULES")
        print("="*80)
        print(f"\n✅ Tổng số alert groups: {len(groups)}\n")
        
        total_rules = 0
        for group in groups:
            rules = group.get('rules', [])
            total_rules += len(rules)
            print(f"📁 Group: {group.get('name')}")
            print(f"   Interval: {group.get('interval', 'N/A')}")
            print(f"   Số lượng rules: {len(rules)}")
            
            # Đếm alerts và recording rules
            alerts = [r for r in rules if r.get('type') == 'alerting']
            recordings = [r for r in rules if r.get('type') == 'recording']
            
            if alerts:
                print(f"   - Alerting rules: {len(alerts)}")
            if recordings:
                print(f"   - Recording rules: {len(recordings)}")
            
            # Hiển thị một vài alerts đầu tiên
            if alerts:
                print("   Alerts:")
                for alert in alerts[:5]:
                    name = alert.get('name', 'Unknown')
                    state = alert.get('state', 'unknown')
                    health = alert.get('health', 'unknown')
                    print(f"     • {name} [{state}] ({health})")
                if len(alerts) > 5:
                    print(f"     ... và {len(alerts) - 5} alerts khác")
            print()
        
        print(f"📊 Tổng số alert rules: {total_rules}")
        print("\n" + "="*80)
        print("💡 Xem chi tiết tại: http://localhost:9090/rules")
        print("="*80)
        
    else:
        print(f"❌ Lỗi HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Lỗi: {e}")
    print("   Đảm bảo Prometheus đang chạy: docker-compose up -d prometheus")


