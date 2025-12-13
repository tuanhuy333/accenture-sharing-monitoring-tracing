#!/usr/bin/env python3
"""
Script để test các alerts trong hệ thống monitoring
"""

import requests
import time
import sys

# URLs của các services
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

PROMETHEUS_URL = 'http://localhost:9090'
ALERTMANAGER_URL = 'http://localhost:9093'


def check_service_health(service_name, url):
    """Kiểm tra service có đang chạy không"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
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
        print(f"❌ Không thể kết nối Prometheus: {e}")
        return []


def check_alertmanager_alerts():
    """Kiểm tra alerts trong Alertmanager"""
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/api/v2/alerts", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"❌ Không thể kết nối Alertmanager: {e}")
        return []


def print_alerts(alerts, source="Prometheus"):
    """In danh sách alerts"""
    if not alerts:
        print(f"\n✅ Không có alerts nào trong {source}")
        return
    
    print(f"\n📊 Alerts trong {source}:")
    print("-" * 80)
    
    for alert in alerts:
        if source == "Prometheus":
            state = alert.get('state', 'unknown')
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            alertname = labels.get('alertname', 'Unknown')
            severity = labels.get('severity', 'unknown')
        else:  # Alertmanager
            state = alert.get('status', {}).get('state', 'unknown')
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            alertname = labels.get('alertname', 'Unknown')
            severity = labels.get('severity', 'unknown')
        
        state_icon = "🔴" if state == "firing" else "🟡" if state == "pending" else "⚪"
        severity_icon = "🚨" if severity == "critical" else "⚠️" if severity == "warning" else "ℹ️"
        
        print(f"{state_icon} [{state.upper()}] {severity_icon} {alertname}")
        print(f"   Severity: {severity}")
        if annotations.get('summary'):
            print(f"   Summary: {annotations['summary']}")
        if annotations.get('description'):
            print(f"   Description: {annotations['description']}")
        print()


def generate_traffic_to_services(count=100, delay=0.1):
    """Generate traffic đến tất cả services để tạo metrics"""
    print(f"\n🚀 Đang tạo traffic đến các services ({count} requests mỗi service)...")
    
    endpoints = [
        # Order Service
        ('order-service', '/', 'GET'),
        ('order-service', '/health', 'GET'),
        ('order-service', '/orders', 'GET'),
        ('order-service', '/orders?user_id=1', 'GET'),
        ('order-service', '/orders/1', 'GET'),
        ('order-service', '/orders/2', 'GET'),
        ('order-service', '/orders', 'POST'),
        
        # User Service
        ('user-service', '/', 'GET'),
        ('user-service', '/health', 'GET'),
        ('user-service', '/users', 'GET'),
        ('user-service', '/users/1', 'GET'),
        
        # Payment Service
        ('payment-service', '/', 'GET'),
        ('payment-service', '/health', 'GET'),
        ('payment-service', '/payments', 'GET'),
        
        # Inventory Service
        ('inventory-service', '/', 'GET'),
        ('inventory-service', '/health', 'GET'),
        ('inventory-service', '/inventory/1', 'GET'),
    ]
    
    total_requests = 0
    for i in range(count):
        for service_name, endpoint, method in endpoints:
            if service_name not in SERVICES:
                continue
                
            url = f"{SERVICES[service_name]}{endpoint}"
            try:
                if method == 'GET':
                    response = requests.get(url, timeout=5)
                elif method == 'POST':
                    response = requests.post(url, json={"user_id": 1, "total": 99.99}, timeout=5)
                total_requests += 1
                if total_requests % 20 == 0:
                    print(f"   Đã gửi {total_requests} requests...")
            except Exception as e:
                pass
            time.sleep(delay)
    
    print(f"✅ Đã gửi tổng cộng {total_requests} requests")
    print("   Đợi 30 giây để Prometheus scrape metrics...")
    time.sleep(30)
    print("   Kiểm tra metrics tại: http://localhost:9090/graph?g0.expr=http_requests_total")


def check_prometheus_metrics():
    """Kiểm tra metrics trong Prometheus"""
    print("\n📊 Kiểm tra metrics trong Prometheus...")
    
    queries = [
        ('http_requests_total', 'Tổng số HTTP requests'),
        ('rate(http_requests_total[5m])', 'Rate của HTTP requests'),
        ('up', 'Trạng thái services'),
    ]
    
    for query, description in queries:
        try:
            response = requests.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={'query': query},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', {}).get('result', [])
                if results:
                    print(f"✅ {description}: Có {len(results)} metrics")
                    # Hiển thị một vài ví dụ
                    for i, result in enumerate(results[:3]):
                        labels = result.get('metric', {})
                        value = result.get('value', [None, '0'])[1]
                        print(f"   - {labels.get('job', 'unknown')}: {value}")
                else:
                    print(f"⚠️  {description}: Không có dữ liệu (metrics = 0)")
        except Exception as e:
            print(f"❌ Lỗi khi query {query}: {e}")


def test_high_error_rate():
    """Test High Error Rate alert bằng cách gửi nhiều request"""
    print("\n🧪 Testing High Error Rate Alert...")
    print("Gửi nhiều request đến order-service...")
    
    order_service_url = SERVICES['order-service']
    for i in range(50):
        try:
            # Gửi request đến endpoint có thể gây lỗi
            requests.get(f"{order_service_url}/orders/99999", timeout=2)
        except:
            pass
        time.sleep(0.1)
    
    print("✅ Đã gửi 50 requests. Đợi 2 phút để alert kích hoạt...")
    print("   Kiểm tra tại: http://localhost:9090/alerts")


def main():
    print("=" * 80)
    print("🔍 KIỂM TRA ALERTS HỆ THỐNG MONITORING")
    print("=" * 80)
    
    # Kiểm tra kết nối Prometheus
    print("\n1️⃣ Kiểm tra kết nối Prometheus...")
    try:
        response = requests.get(f"{PROMETHEUS_URL}/-/healthy", timeout=5)
        if response.status_code == 200:
            print("✅ Prometheus đang chạy")
        else:
            print("❌ Prometheus không phản hồi đúng")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Không thể kết nối Prometheus: {e}")
        print("   Đảm bảo Prometheus đang chạy: docker-compose up -d prometheus")
        sys.exit(1)
    
    # Kiểm tra kết nối Alertmanager
    print("\n2️⃣ Kiểm tra kết nối Alertmanager...")
    try:
        response = requests.get(f"{ALERTMANAGER_URL}/-/healthy", timeout=5)
        if response.status_code == 200:
            print("✅ Alertmanager đang chạy")
        else:
            print("❌ Alertmanager không phản hồi đúng")
    except Exception as e:
        print(f"⚠️  Không thể kết nối Alertmanager: {e}")
        print("   Đảm bảo Alertmanager đang chạy: docker-compose up -d alertmanager")
    
    # Kiểm tra trạng thái services
    print("\n3️⃣ Kiểm tra trạng thái các services...")
    for service_name, url in SERVICES.items():
        if check_service_health(service_name, url):
            print(f"✅ {service_name}: UP")
        else:
            print(f"❌ {service_name}: DOWN")
    
    # Kiểm tra alerts trong Prometheus
    print("\n4️⃣ Kiểm tra alerts trong Prometheus...")
    prometheus_alerts = check_prometheus_alerts()
    print_alerts(prometheus_alerts, "Prometheus")
    
    # Kiểm tra alerts trong Alertmanager
    print("\n5️⃣ Kiểm tra alerts trong Alertmanager...")
    alertmanager_alerts = check_alertmanager_alerts()
    print_alerts(alertmanager_alerts, "Alertmanager")
    
    # Kiểm tra metrics
    print("\n6️⃣ Kiểm tra metrics trong Prometheus...")
    check_prometheus_metrics()
    
    # Menu tương tác
    print("\n" + "=" * 80)
    print("📋 MENU TEST ALERTS")
    print("=" * 80)
    print("1. Generate Traffic (Tạo metrics) - QUAN TRỌNG nếu metrics = 0")
    print("2. Test High Error Rate Alert")
    print("3. Kiểm tra metrics trong Prometheus")
    print("4. Xem tất cả alerts trong Prometheus")
    print("5. Xem tất cả alerts trong Alertmanager")
    print("6. Thoát")
    
    choice = input("\nChọn option (1-6): ").strip()
    
    if choice == "1":
        generate_traffic_to_services(count=100, delay=0.1)
        print("\n✅ Đã tạo traffic. Kiểm tra lại metrics:")
        check_prometheus_metrics()
    elif choice == "2":
        test_high_error_rate()
    elif choice == "3":
        check_prometheus_metrics()
    elif choice == "4":
        print("\n🌐 Mở trình duyệt tại: http://localhost:9090/alerts")
    elif choice == "5":
        print("\n🌐 Mở trình duyệt tại: http://localhost:9093")
    elif choice == "6":
        print("👋 Tạm biệt!")
    else:
        print("❌ Lựa chọn không hợp lệ")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy bỏ")
        sys.exit(0)

