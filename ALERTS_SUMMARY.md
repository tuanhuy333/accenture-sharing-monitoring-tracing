# 📋 Tóm tắt Alert Rules

## ⏱️ Thời gian Alert: 30 giây

Tất cả alerts sẽ kích hoạt sau **30 giây** (trừ một số trường hợp đặc biệt).

---

## 🚨 CRITICAL Alerts (Mức độ nghiêm trọng cao)

### Service Down Alerts (30s)
- `UserServiceDown` - User service không phản hồi
- `OrderServiceDown` - Order service không phản hồi
- `PaymentServiceDown` - Payment service không phản hồi
- `InventoryServiceDown` - Inventory service không phản hồi
- `ShippingServiceDown` - Shipping service không phản hồi
- `AuthServiceDown` - Auth service không phản hồi

### Error Rate Alerts (30s)
- `HighErrorRate` - Tỷ lệ lỗi 5xx > 0.1 req/s
- `ErrorRateSpike` - Tỷ lệ lỗi tăng đột biến (gấp 3 lần)
- `VeryHighRequestLatency` - Độ trễ 95th percentile > 2 giây
- `ServiceUnavailable` - Tỷ lệ lỗi > 10% tổng requests

### Prometheus Monitoring (1m)
- `PrometheusScrapeFailure` - Không thể scrape metrics từ target

---

## ⚠️ WARNING Alerts (Mức độ cảnh báo)

### Service Down Alerts (30s)
- `NotificationServiceDown` - Notification service không phản hồi
- `ReviewServiceDown` - Review service không phản hồi

### Error Rate Alerts (30s)
- `High4xxErrorRate` - Tỷ lệ lỗi 4xx > 0.5 req/s
- `ServiceDegraded` - Tỷ lệ lỗi > 5% tổng requests (1m)

### Latency Alerts (30s)
- `HighRequestLatency` - Độ trễ 95th percentile > 1 giây
- `SlowResponseTime` - Độ trễ 99th percentile > 3 giây

### Request Rate Alerts
- `HighRequestRate` - Request rate > 10 req/s (30s)
- `LowRequestRate` - Request rate < 0.01 req/s (2m)
- `RequestRateSpike` - Request rate tăng đột biến (30s)

### Active Requests Alerts (30s)
- `HighActiveRequests` - Số lượng active requests > 50

### Prometheus Monitoring (30s)
- `PrometheusTargetDown` - Prometheus target không phản hồi

---

## 📊 Phân loại Alerts

### 1. Service Availability (8 alerts)
- Kiểm tra service có đang chạy không
- Thời gian: 30s

### 2. Error Rate (3 alerts)
- `HighErrorRate` - Lỗi 5xx cao
- `High4xxErrorRate` - Lỗi 4xx cao
- `ErrorRateSpike` - Lỗi tăng đột biến

### 3. Latency (3 alerts)
- `HighRequestLatency` - Độ trễ cao (95th percentile)
- `VeryHighRequestLatency` - Độ trễ rất cao
- `SlowResponseTime` - Thời gian phản hồi chậm (99th percentile)

### 4. Request Rate (3 alerts)
- `HighRequestRate` - Request rate cao
- `LowRequestRate` - Request rate thấp
- `RequestRateSpike` - Request rate tăng đột biến

### 5. Service Health (2 alerts)
- `ServiceUnavailable` - Service không khả dụng
- `ServiceDegraded` - Service suy giảm

### 6. Active Requests (1 alert)
- `HighActiveRequests` - Số lượng active requests cao

### 7. Prometheus Monitoring (2 alerts)
- `PrometheusTargetDown` - Target down
- `PrometheusScrapeFailure` - Scrape thất bại

---

## 🧪 Cách Test Alerts

### Test Service Down Alert:
```bash
docker-compose stop order-service
# Đợi 30 giây, alert sẽ kích hoạt
```

### Test High Error Rate:
```bash
# Tạo nhiều requests với lỗi
python quick_generate_traffic.py
# Hoặc dừng một service phụ thuộc
```

### Test High Latency:
```bash
# Tạo nhiều requests đồng thời
python quick_generate_traffic.py
```

### Test Request Rate Spike:
```bash
# Tạo burst traffic
for i in {1..100}; do curl http://localhost:8001/orders & done
```

---

## 📧 Email Notifications

- **Critical alerts**: Gửi đến `email-critical` receiver
- **Warning alerts**: Gửi đến `email-warning` receiver
- **All alerts**: Gửi đến `email-notifications` receiver

Email nhận: `tuanhuy030799@gmail.com`

---

## 🔍 Kiểm tra Alerts

### Xem tất cả alerts:
- Prometheus: http://localhost:9090/alerts
- Alertmanager: http://localhost:9093

### Xem alert rules:
- Prometheus: http://localhost:9090/rules

### Xem metrics:
- Prometheus: http://localhost:9090/graph

---

## 📝 Lưu ý

1. **Thời gian alert**: Hầu hết alerts kích hoạt sau 30 giây
2. **Evaluation interval**: Prometheus đánh giá alerts mỗi 30 giây
3. **Scrape interval**: Prometheus scrape metrics mỗi 15 giây
4. **Email delay**: Email có thể đến sau 10-30 giây sau khi alert firing


