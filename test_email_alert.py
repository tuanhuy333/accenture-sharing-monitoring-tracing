#!/usr/bin/env python3
"""
Script để test email alert bằng cách trigger một alert
"""

import requests
import time
import sys

PROMETHEUS_URL = 'http://localhost:9090'
ALERTMANAGER_URL = 'http://localhost:9093'

def check_alertmanager_status():
    """Kiểm tra Alertmanager có đang chạy không"""
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/-/healthy", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_prometheus_alerts():
    """Kiểm tra alerts trong Prometheus"""
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/alerts", timeout=5)
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('data', {}).get('alerts', [])
            return alerts
        return []
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return []

def check_alertmanager_alerts():
    """Kiểm tra alerts trong Alertmanager"""
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return []

def print_alerts(alerts, source="Prometheus"):
    """In danh sách alerts"""
    if not alerts:
        print(f"\n⚪ Không có alerts nào trong {source}")
        return
    
    print(f"\n📊 Alerts trong {source}:")
    print("-" * 80)
    
    firing_count = 0
    for alert in alerts:
        if source == "Prometheus":
            state = alert.get('state', 'unknown')
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
        else:  # Alertmanager
            state = alert.get('status', {}).get('state', 'unknown')
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
        
        if state == "firing":
            firing_count += 1
            alertname = labels.get('alertname', 'Unknown')
            severity = labels.get('severity', 'unknown')
            job = labels.get('job', 'unknown')
            
            state_icon = "🔴"
            severity_icon = "🚨" if severity == "critical" else "⚠️" if severity == "warning" else "ℹ️"
            
            print(f"{state_icon} [{state.upper()}] {severity_icon} {alertname}")
            print(f"   Service: {job}")
            print(f"   Severity: {severity}")
            if annotations.get('summary'):
                print(f"   Summary: {annotations['summary']}")
            if annotations.get('description'):
                print(f"   Description: {annotations['description']}")
            print()
    
    if firing_count == 0:
        print("⚪ Không có alerts nào đang FIRING")
    else:
        print(f"✅ Tìm thấy {firing_count} alerts đang FIRING")
        print("   Email sẽ được gửi trong vài giây...")

def main():
    print("=" * 80)
    print("🧪 TEST EMAIL ALERT")
    print("=" * 80)
    
    # Kiểm tra Alertmanager
    print("\n1️⃣ Kiểm tra Alertmanager...")
    if check_alertmanager_status():
        print("✅ Alertmanager đang chạy")
    else:
        print("❌ Alertmanager không chạy!")
        print("   Khởi động: docker-compose up -d alertmanager")
        sys.exit(1)
    
    # Kiểm tra alerts trong Prometheus
    print("\n2️⃣ Kiểm tra alerts trong Prometheus...")
    prometheus_alerts = check_prometheus_alerts()
    print_alerts(prometheus_alerts, "Prometheus")
    
    # Kiểm tra alerts trong Alertmanager
    print("\n3️⃣ Kiểm tra alerts trong Alertmanager...")
    alertmanager_alerts = check_alertmanager_alerts()
    print_alerts(alertmanager_alerts, "Alertmanager")
    
    # Hướng dẫn test
    print("\n" + "=" * 80)
    print("💡 ĐỂ TEST EMAIL ALERT:")
    print("=" * 80)
    print("1. Dừng một service để trigger alert:")
    print("   docker-compose stop order-service")
    print()
    print("2. Đợi 1 phút để alert kích hoạt")
    print()
    print("3. Kiểm tra:")
    print("   - Prometheus: http://localhost:9090/alerts")
    print("   - Alertmanager: http://localhost:9093")
    print("   - Email: tuanhuy030799@gmail.com (kể cả spam)")
    print()
    print("4. Xem logs Alertmanager:")
    print("   docker-compose logs -f alertmanager")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy bỏ")
        sys.exit(0)


