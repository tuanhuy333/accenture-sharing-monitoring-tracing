#!/usr/bin/env python3
"""Kiểm tra metrics trong Prometheus"""

import requests
import time
import json

PROMETHEUS_URL = 'http://localhost:9090'

print("⏳ Đợi 15 giây để Prometheus scrape metrics...")
time.sleep(15)

print("\n📊 Kiểm tra metrics trong Prometheus...\n")

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
                for i, result in enumerate(results[:5]):
                    labels = result.get('metric', {})
                    value = result.get('value', [None, '0'])[1]
                    job = labels.get('job', 'unknown')
                    service = labels.get('service', '')
                    status = labels.get('status', '')
                    print(f"   - {job}{' (' + service + ')' if service else ''}{' status=' + status if status else ''}: {value}")
            else:
                print(f"⚠️  {description}: Không có dữ liệu (metrics = 0)")
        else:
            print(f"❌ Lỗi khi query {query}: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Lỗi khi query {query}: {e}")

print("\n" + "="*80)
print("💡 Nếu metrics vẫn = 0:")
print("   1. Kiểm tra Prometheus targets: http://localhost:9090/targets")
print("   2. Chạy lại: python quick_generate_traffic.py")
print("   3. Đợi thêm 30 giây để Prometheus scrape")
print("="*80)


