# Hướng Dẫn Sử Dụng Grafana Dashboards

## 📊 Tổng Quan

Hệ thống có 5 dashboards chính để monitor microservices:

1. **Microservices Overview Dashboard** - Tổng quan toàn hệ thống
2. **Logs Dashboard** - Xem logs từ Loki
3. **Traces Dashboard** - Xem traces từ Tempo
4. **Service Detail Dashboard** - Chi tiết từng service
5. **Microservices Monitoring Dashboard** - Dashboard gốc (có sẵn)

## 🚀 Truy Cập Dashboards

1. Mở Grafana: http://localhost:3000
2. Đăng nhập: `admin` / `admin`
3. Vào **Dashboards** → Chọn dashboard muốn xem

## 📋 Chi Tiết Từng Dashboard

### 1. Microservices Overview Dashboard

**Mục đích:** Tổng quan toàn bộ hệ thống với tất cả services

**Panels:**
- **Service Health Status**: Trạng thái up/down của tất cả services
- **Request Rate by Service**: Số lượng requests/giây theo từng service
- **Response Time (p95, p99)**: Thời gian phản hồi (percentile 95 và 99)
- **Error Rate by Service**: Tỷ lệ lỗi theo từng service
- **Active Requests by Service**: Số requests đang xử lý
- **Total Requests by Status Code**: Tổng số requests theo HTTP status code
- **Request Rate by HTTP Method**: Số lượng requests theo method (GET, POST, etc.)

**Variables:**
- `service`: Filter theo service (có thể chọn nhiều hoặc "All")

**Refresh:** 10 giây

### 2. Logs Dashboard

**Mục đích:** Xem và phân tích logs từ tất cả services

**Panels:**
- **Logs**: Hiển thị logs real-time với search và filter
- **Log Volume by Service**: Biểu đồ số lượng logs theo thời gian
- **Error Log Volume**: Số lượng error logs theo thời gian
- **Error Logs Only**: Chỉ hiển thị logs có lỗi

**Variables:**
- `service`: Filter theo service (có thể chọn nhiều hoặc "All")
- `filter`: Text filter để tìm kiếm trong logs

**Cách sử dụng:**
- Chọn service từ dropdown
- Nhập từ khóa vào filter box để tìm kiếm
- Click vào log entry để xem chi tiết

### 3. Traces Dashboard

**Mục đích:** Xem distributed traces và service map

**Panels:**
- **Traces**: Hiển thị traces với service map và trace timeline
- **Trace Rate by Service**: Số lượng traces/giây
- **Trace Latency (p95, p99)**: Độ trễ của traces

**Variables:**
- `service`: Filter theo service

**Tính năng:**
- Click vào trace để xem chi tiết
- Xem service map để hiểu flow giữa các services
- Link đến logs liên quan (traces to logs)
- Link đến metrics liên quan (traces to metrics)

### 4. Service Detail Dashboard

**Mục đích:** Chi tiết sâu về một service cụ thể

**Panels:**
- **Service Status**: Trạng thái up/down
- **Request Rate**: Số requests/giây
- **Response Time (p95)**: Thời gian phản hồi
- **Error Rate**: Tỷ lệ lỗi
- **Request Rate by Endpoint**: Requests theo từng endpoint
- **Response Time Distribution**: Phân bố thời gian phản hồi (p50, p95, p99)
- **Total Requests by Status Code**: Tổng requests theo status code
- **Recent Logs**: Logs gần đây của service

**Variables:**
- `service`: Chọn service muốn xem chi tiết

**Links:**
- "View Logs": Mở Explore với logs của service
- "View Traces": Mở Explore với traces của service

### 5. Microservices Monitoring Dashboard

**Mục đích:** Dashboard gốc với các metrics cơ bản

**Panels:**
- HTTP Requests Rate
- HTTP Request Duration (95th percentile)
- Error Rate
- Active Requests
- Service Health Status

## 💡 Tips Sử Dụng

### 1. Sử dụng Variables

- Click vào dropdown ở đầu dashboard để filter
- Có thể chọn nhiều services cùng lúc
- "All" để xem tất cả

### 2. Time Range

- Mặc định: "Last 15 minutes"
- Có thể thay đổi ở góc trên bên phải
- "Last 1 hour", "Last 6 hours", "Last 24 hours", etc.

### 3. Drill Down

- Từ Overview → Service Detail: Chọn service và xem chi tiết
- Từ Service Detail → Logs/Traces: Click links ở đầu dashboard
- Từ Traces → Logs: Click vào span để xem logs liên quan

### 4. Alerting

- Các alerts được cấu hình trong Prometheus
- Xem alerts trong Alertmanager: http://localhost:9093
- Hoặc trong Grafana: Alerting → Alert Rules

## 🔧 Tùy Chỉnh Dashboard

### Thêm Panel Mới

1. Click "Add" → "Visualization"
2. Chọn datasource (Prometheus, Loki, hoặc Tempo)
3. Nhập query
4. Chọn visualization type
5. Save dashboard

### Chỉnh Sửa Panel

1. Click vào panel → "Edit"
2. Thay đổi query hoặc visualization
3. Save dashboard

### Export/Import Dashboard

1. Click vào dashboard settings (⚙️)
2. "JSON Model" để xem/copy JSON
3. "Save dashboard" để lưu
4. Có thể export để backup hoặc share

## 📊 Metrics Có Sẵn

### Prometheus Metrics

- `http_requests_total`: Tổng số HTTP requests
- `http_request_duration_seconds`: Thời gian xử lý request (histogram)
- `active_requests`: Số requests đang xử lý (gauge)
- `up`: Trạng thái service (1 = up, 0 = down)

### Loki Logs

- Logs từ tất cả services với labels: `service`, `job`
- Có thể query bằng LogQL

### Tempo Traces

- Distributed traces với service map
- Metrics: `tempo_spanmetrics_calls_total`, `tempo_spanmetrics_latency_bucket`

## 🚨 Troubleshooting

### Dashboard không hiển thị data

1. **Kiểm tra time range**: Đảm bảo có data trong khoảng thời gian đó
2. **Kiểm tra variables**: Service được chọn có đúng không
3. **Kiểm tra datasource**: Prometheus/Loki/Tempo có đang chạy không
4. **Tạo traffic**: Chạy `python scripts/generate_traffic.py` để có data

### Query không hoạt động

1. Kiểm tra syntax của query
2. Kiểm tra labels có đúng không: `label_values(http_requests_total, service)`
3. Xem query inspector để debug

### Dashboard không load

1. Kiểm tra Grafana logs: `docker logs grafana`
2. Kiểm tra file JSON có đúng format không
3. Restart Grafana: `docker-compose restart grafana`

## 🔗 Liên Kết Hữu Ích

- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Loki: http://localhost:3100
- Tempo: http://localhost:3200
- Alertmanager: http://localhost:9093

## 📚 Tài Liệu Tham Khảo

- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL](https://grafana.com/docs/loki/latest/logql/)
- [TraceQL](https://grafana.com/docs/tempo/latest/traceql/)

