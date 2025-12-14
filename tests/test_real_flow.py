#!/usr/bin/env python3
"""
Test luồng thực tế: Request → Error → Trace → Logs → Dashboard

Luồng hoạt động:
1. Tạo request đi qua các services (như trong thực tế)
2. Inject error vào payment-service
3. Hiển thị trace ID và link để xem trace
4. Hiển thị vị trí log files
5. Hiển thị link đến dashboard
"""

import requests
import json
import time
import uuid
import os
from datetime import datetime

# URLs
ORDER_SERVICE_URL = "http://localhost:8001"
GRAFANA_URL = "http://localhost:3000"
PROMETHEUS_URL = "http://localhost:9090"
LOKI_URL = "http://localhost:3100"

# Log paths
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

def print_section(title):
    """In tiêu đề section"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def check_service_health():
    """Kiểm tra services có đang chạy không"""
    services = {
        "Order Service": ORDER_SERVICE_URL,
        "Grafana": GRAFANA_URL,
        "Prometheus": PROMETHEUS_URL
    }
    
    print("\n🔍 Kiểm tra services...")
    all_healthy = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code in [200, 404]:  # 404 is OK, service is running
                print(f"   ✅ {name}: Running")
            else:
                print(f"   ⚠️  {name}: Status {response.status_code}")
                all_healthy = False
        except:
            print(f"   ❌ {name}: Not accessible")
            all_healthy = False
    
    return all_healthy

def make_request():
    """Bước 1: Tạo request như trong thực tế"""
    print_section("📦 BƯỚC 1: TẠO REQUEST")
    
    request_id = str(uuid.uuid4())[:8]
    print(f"Request ID: {request_id}")
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nĐang gửi request đến Order Service...")
    print("   Flow: Order Service → Inventory Service → Payment Service")
    
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
        
        print(f"\n   Status Code: {response.status_code}")
        
        if response.status_code == 500:
            data = response.json()
            trace_id = data.get('trace_id', 'N/A')
            
            print(f"   ✅ Error đã được trigger!")
            print(f"   Error: {data.get('error', 'Unknown error')}")
            
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
                    trace_id = order['payment_trace_id']
            
            return trace_id, request_id, True
        elif response.status_code == 201:
            data = response.json()
            trace_id = data.get('trace_id', 'N/A')
            print(f"   ⚠️  Order created successfully (no error)")
            print(f"   Trace ID: {trace_id}")
            print(f"   Note: Error was not injected. Services may need restart.")
            return trace_id, request_id, False
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, request_id, False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        print(f"   Make sure services are running: docker-compose up -d")
        return None, request_id, False

def show_trace_info(trace_id):
    """Bước 2: Hiển thị thông tin trace"""
    print_section("🔍 BƯỚC 2: XEM TRACE")
    
    if not trace_id or trace_id == 'N/A':
        print("   ⚠️  Không có trace ID")
        return
    
    print(f"Trace ID: {trace_id}")
    print("\n📊 Các cách xem trace:")
    
    # Link 1: Grafana Explore với TraceQL query
    traceql_query = f'{{traceID="{trace_id}"}}'
    panes_json = json.dumps({
        "9nf": {
            "datasource": "tempo",
            "queries": [{
                "query": traceql_query,
                "queryType": "traceql",
                "refId": "A",
                "limit": 20,
                "tableType": "traces"
            }],
            "range": {"from": "now-15m", "to": "now"}
        }
    })
    import urllib.parse
    panes_encoded = urllib.parse.quote(panes_json)
    grafana_trace_url = f"{GRAFANA_URL}/explore?schemaVersion=1&panes={panes_encoded}&orgId=1"
    
    print(f"\n   1. Xem trace cụ thể (Trace ID):")
    print(f"      {grafana_trace_url}")
    
    # Link 2: Grafana Explore với error traces
    error_traces_url = f"{GRAFANA_URL}/explore?schemaVersion=1&panes=%7B%224hj%22%3A%7B%22datasource%22%3A%22tempo%22%2C%22queries%22%3A%5B%7B%22queryType%22%3A%22traceqlSearch%22%2C%22query%22%3A%22%7B%20service.name%20%3D%20%5C%22payment-service%5C%22%20%26%26%20status%20%3D%20%5C%22error%5C%22%20%7D%22%2C%22refId%22%3A%22A%22%2C%22datasource%22%3A%7B%22type%22%3A%22tempo%22%2C%22uid%22%3A%22tempo%22%7D%2C%22limit%22%3A20%2C%22tableType%22%3A%22traces%22%7D%5D%2C%22range%22%3A%7B%22from%22%3A%22now-15m%22%2C%22to%22%3A%22now%22%7D%7D%7D&orgId=1"
    print(f"\n   2. Xem tất cả error traces của payment-service:")
    print(f"      {error_traces_url}")
    
    # Link 3: Grafana Explore đơn giản
    simple_url = f"{GRAFANA_URL}/explore?orgId=1&left=%5B%22now-15m%22,%22now%22,%22Tempo%22%5D"
    print(f"\n   3. Grafana Explore (tự search):")
    print(f"      {simple_url}")
    print(f"      → Nhập trace ID: {trace_id}")
    print(f"      → Hoặc query: {{traceID=\"{trace_id}\"}}")
    
    print(f"\n   💡 Tip: Đợi 5-10 giây để trace được index trong Tempo")

def show_logs_info(request_id):
    """Bước 3: Hiển thị thông tin logs"""
    print_section("📋 BƯỚC 3: XEM LOGS")
    
    print("Log files được lưu tại:")
    print(f"   {LOG_DIR}")
    
    print("\nCác log files liên quan:")
    log_files = [
        ("order-service.log", "Order Service logs"),
        ("payment-service.log", "Payment Service logs (có error)"),
        ("inventory-service.log", "Inventory Service logs")
    ]
    
    for log_file, description in log_files:
        log_path = os.path.join(LOG_DIR, log_file)
        if os.path.exists(log_path):
            print(f"\n   ✅ {description}:")
            print(f"      {log_path}")
            # Đọc vài dòng cuối cùng
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"      (Last line: {lines[-1].strip()[:100]}...)")
            except:
                pass
        else:
            print(f"\n   ⚠️  {description}: File chưa tồn tại")
    
    print(f"\n   💡 Để xem logs real-time:")
    print(f"      docker-compose logs -f order-service payment-service")
    print(f"      hoặc tail -f {LOG_DIR}/payment-service.log")

def show_dashboard_info():
    """Bước 4: Hiển thị thông tin dashboard"""
    print_section("📊 BƯỚC 4: XEM DASHBOARD")
    
    print("Các dashboard có sẵn:")
    
    dashboards = [
        ("Microservices Dashboard", f"{GRAFANA_URL}/d/microservices"),
        ("Demo Dashboard", f"{GRAFANA_URL}/d/demo"),
    ]
    
    for name, url in dashboards:
        print(f"\n   📈 {name}:")
        print(f"      {url}")
    
    print(f"\n   📊 Prometheus Alerts:")
    print(f"      {PROMETHEUS_URL}/alerts")
    
    print(f"\n   📧 Alertmanager:")
    print(f"      http://localhost:9093")
    
    print(f"\n   💡 Tip: Dashboard sẽ tự động cập nhật metrics và traces")

def main():
    """Chạy test luồng thực tế"""
    print("\n" + "="*80)
    print("  🚀 TEST LUỒNG THỰC TẾ")
    print("  Request → Error → Trace → Logs → Dashboard")
    print("="*80)
    
    # Kiểm tra services
    if not check_service_health():
        print("\n⚠️  Một số services không khả dụng. Vẫn tiếp tục test...")
    
    # Bước 1: Tạo request
    trace_id, request_id, error_triggered = make_request()
    
    if not error_triggered:
        print("\n⚠️  Error không được trigger. Kiểm tra lại services.")
        return
    
    # Đợi một chút để trace được gửi
    print("\n⏳ Đợi 3 giây để trace được gửi đến Tempo...")
    time.sleep(3)
    
    # Bước 2: Hiển thị trace info
    show_trace_info(trace_id)
    
    # Bước 3: Hiển thị logs info
    show_logs_info(request_id)
    
    # Bước 4: Hiển thị dashboard info
    show_dashboard_info()
    
    # Tóm tắt
    print_section("✅ HOÀN TẤT")
    print("Luồng test đã hoàn thành!")
    print("\n📋 Tóm tắt:")
    print(f"   • Request ID: {request_id}")
    print(f"   • Trace ID: {trace_id}")
    print(f"   • Error đã được trigger: ✅")
    print(f"   • Logs: {LOG_DIR}")
    print(f"   • Grafana: {GRAFANA_URL}")
    print("\n💡 Next steps:")
    print("   1. Mở Grafana và xem trace")
    print("   2. Kiểm tra logs trong thư mục logs/")
    print("   3. Xem dashboard để theo dõi metrics")
    print("   4. Đợi 10-20 giây để alert được gửi qua email")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy bỏ")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


