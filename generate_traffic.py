#!/usr/bin/env python3
"""
Script để generate traffic đến các services để tạo metrics cho Prometheus
Chạy script này nếu metrics trong Prometheus đều là 0
"""

import requests
import time
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# Endpoints cho mỗi service
ENDPOINTS = {
    'order-service': [
        ('/', 'GET'),
        ('/health', 'GET'),
        ('/orders', 'GET'),
        ('/orders?user_id=1', 'GET'),
        ('/orders/1', 'GET'),
        ('/orders/2', 'GET'),
        ('/orders/3', 'GET'),
        ('/orders', 'POST'),
    ],
    'user-service': [
        ('/', 'GET'),
        ('/health', 'GET'),
        ('/users', 'GET'),
        ('/users/1', 'GET'),
        ('/users/2', 'GET'),
        ('/users/1/orders', 'GET'),
    ],
    'payment-service': [
        ('/', 'GET'),
        ('/health', 'GET'),
        ('/payments', 'GET'),
        ('/payments?order_id=1', 'GET'),
        ('/payments/1', 'GET'),
        ('/payments', 'POST'),
    ],
    'inventory-service': [
        ('/', 'GET'),
        ('/health', 'GET'),
        ('/inventory/1', 'GET'),
        ('/inventory/2', 'GET'),
    ],
    'shipping-service': [
        ('/', 'GET'),
        ('/health', 'GET'),
    ],
    'notification-service': [
        ('/', 'GET'),
        ('/health', 'GET'),
    ],
    'review-service': [
        ('/', 'GET'),
        ('/health', 'GET'),
    ],
    'auth-service': [
        ('/', 'GET'),
        ('/health', 'GET'),
    ],
}


def make_request(service_name, endpoint, method):
    """Gửi một request đến service"""
    if service_name not in SERVICES:
        return None
    
    url = f"{SERVICES[service_name]}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            data = {"user_id": 1, "total": 99.99} if 'order' in endpoint else {"order_id": 1, "amount": 99.99}
            response = requests.post(url, json=data, timeout=5)
        return response.status_code
    except Exception as e:
        return None


def check_service_available(service_name):
    """Kiểm tra service có đang chạy không"""
    if service_name not in SERVICES:
        return False
    try:
        response = requests.get(f"{SERVICES[service_name]}/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def generate_traffic_sequential(total_requests=200, delay=0.05):
    """Generate traffic tuần tự"""
    print(f"🚀 Đang tạo {total_requests} requests đến các services...")
    print("   (Chế độ tuần tự - chậm nhưng ổn định)\n")
    
    available_services = [s for s in SERVICES.keys() if check_service_available(s)]
    
    if not available_services:
        print("❌ Không có service nào đang chạy!")
        print("   Khởi động services: docker-compose up -d")
        return
    
    print(f"✅ Tìm thấy {len(available_services)} services đang chạy:")
    for s in available_services:
        print(f"   - {s}")
    print()
    
    request_count = 0
    success_count = 0
    
    for i in range(total_requests):
        # Chọn service và endpoint ngẫu nhiên
        service_name = random.choice(available_services)
        if service_name in ENDPOINTS:
            endpoint, method = random.choice(ENDPOINTS[service_name])
            
            status = make_request(service_name, endpoint, method)
            request_count += 1
            
            if status:
                success_count += 1
            
            if request_count % 50 == 0:
                print(f"   Đã gửi {request_count} requests ({success_count} thành công)...")
            
            time.sleep(delay)
    
    print(f"\n✅ Hoàn thành!")
    print(f"   Tổng requests: {request_count}")
    print(f"   Thành công: {success_count}")
    print(f"   Thất bại: {request_count - success_count}")
    print("\n⏳ Đợi 30 giây để Prometheus scrape metrics...")
    print("   Sau đó kiểm tra tại: http://localhost:9090/graph?g0.expr=http_requests_total")


def generate_traffic_parallel(total_requests=200, max_workers=10):
    """Generate traffic song song (nhanh hơn)"""
    print(f"🚀 Đang tạo {total_requests} requests đến các services...")
    print(f"   (Chế độ song song với {max_workers} workers)\n")
    
    available_services = [s for s in SERVICES.keys() if check_service_available(s)]
    
    if not available_services:
        print("❌ Không có service nào đang chạy!")
        print("   Khởi động services: docker-compose up -d")
        return
    
    print(f"✅ Tìm thấy {len(available_services)} services đang chạy:")
    for s in available_services:
        print(f"   - {s}")
    print()
    
    # Tạo danh sách tasks
    tasks = []
    for _ in range(total_requests):
        service_name = random.choice(available_services)
        if service_name in ENDPOINTS:
            endpoint, method = random.choice(ENDPOINTS[service_name])
            tasks.append((service_name, endpoint, method))
    
    success_count = 0
    request_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, s, e, m) for s, e, m in tasks]
        
        for future in as_completed(futures):
            request_count += 1
            result = future.result()
            if result:
                success_count += 1
            
            if request_count % 50 == 0:
                print(f"   Đã gửi {request_count} requests ({success_count} thành công)...")
    
    print(f"\n✅ Hoàn thành!")
    print(f"   Tổng requests: {request_count}")
    print(f"   Thành công: {success_count}")
    print(f"   Thất bại: {request_count - success_count}")
    print("\n⏳ Đợi 30 giây để Prometheus scrape metrics...")
    print("   Sau đó kiểm tra tại: http://localhost:9090/graph?g0.expr=http_requests_total")


def main():
    print("=" * 80)
    print("🚀 GENERATE TRAFFIC ĐỂ TẠO METRICS CHO PROMETHEUS")
    print("=" * 80)
    print()
    print("Script này sẽ gửi requests đến các services để tạo metrics.")
    print("Chạy script này nếu metrics trong Prometheus đều là 0.\n")
    
    # Kiểm tra services
    print("🔍 Kiểm tra services...")
    available = []
    for service_name in SERVICES.keys():
        if check_service_available(service_name):
            print(f"✅ {service_name}: UP")
            available.append(service_name)
        else:
            print(f"❌ {service_name}: DOWN")
    
    if not available:
        print("\n❌ Không có service nào đang chạy!")
        print("   Khởi động services: docker-compose up -d")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("Chọn chế độ:")
    print("1. Tuần tự (chậm nhưng ổn định) - Khuyến nghị")
    print("2. Song song (nhanh hơn)")
    print("3. Thoát")
    
    choice = input("\nChọn (1-3): ").strip()
    
    if choice == "1":
        count = input("Số lượng requests (mặc định 200): ").strip()
        count = int(count) if count.isdigit() else 200
        generate_traffic_sequential(total_requests=count, delay=0.05)
    elif choice == "2":
        count = input("Số lượng requests (mặc định 200): ").strip()
        count = int(count) if count.isdigit() else 200
        generate_traffic_parallel(total_requests=count, max_workers=10)
    elif choice == "3":
        print("👋 Tạm biệt!")
    else:
        print("❌ Lựa chọn không hợp lệ")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy bỏ")
        sys.exit(0)


