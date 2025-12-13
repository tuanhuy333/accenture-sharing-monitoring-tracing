# Hướng dẫn Thiết lập Cảnh báo (Alerts)

## Tổng quan

Hệ thống monitoring này sử dụng **Prometheus** để thu thập metrics và **Alertmanager** để gửi cảnh báo qua email khi có sự cố xảy ra.

## Các thành phần

1. **Prometheus**: Thu thập metrics từ các services
2. **Alertmanager**: Xử lý và gửi cảnh báo
3. **Alert Rules**: Định nghĩa các điều kiện cảnh báo trong `config/alerts.yml`

## Các loại cảnh báo hiện có

### 1. Service Down Alerts
- Cảnh báo khi một service không phản hồi
- Các services được giám sát:
  - `user-service` (Critical)
  - `order-service` (Critical)
  - `payment-service` (Critical)
  - `inventory-service` (Critical)
  - `shipping-service` (Critical)
  - `auth-service` (Critical)
  - `notification-service` (Warning)
  - `review-service` (Warning)

### 2. High Error Rate Alert
- Cảnh báo khi tỷ lệ lỗi HTTP 5xx > 0.1 requests/giây
- Mức độ: **Critical**
- Thời gian kích hoạt: 2 phút

### 3. High Request Latency Alert
- Cảnh báo khi độ trễ 95th percentile > 1 giây
- Mức độ: **Warning**
- Thời gian kích hoạt: 5 phút

## Cách thiết lập Email Cảnh báo

### Bước 1: Cấu hình Gmail (nếu dùng Gmail)

1. **Bật 2-Factor Authentication (2FA)** cho tài khoản Gmail của bạn
   - Truy cập: https://myaccount.google.com/security
   - Bật "2-Step Verification"

2. **Tạo App Password**
   - Truy cập: https://myaccount.google.com/apppasswords
   - Chọn "Mail" và "Other (Custom name)"
   - Nhập tên: "Alertmanager"
   - Copy mật khẩu được tạo (16 ký tự)

### Bước 2: Cập nhật file `config/alertmanager.yml`

Mở file `config/alertmanager.yml` và thay đổi các giá trị sau:

```yaml
global:
  smtp_from: 'your-email@gmail.com'  # Email của bạn
  smtp_auth_username: 'your-email@gmail.com'  # Email của bạn
  smtp_auth_password: 'your-app-password'  # App Password từ Gmail

receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'recipient@example.com'  # Email nhận cảnh báo
```

**Lưu ý**: Thay `recipient@example.com` bằng email bạn muốn nhận cảnh báo.

### Bước 3: Khởi động lại Alertmanager

```bash
docker-compose restart alertmanager
```

Hoặc nếu chưa chạy:

```bash
docker-compose up -d alertmanager
```

## Kiểm tra Alerts

### 1. Xem alerts trong Prometheus

Truy cập: http://localhost:9090/alerts

Bạn sẽ thấy danh sách các alerts và trạng thái của chúng:
- **Inactive**: Chưa kích hoạt
- **Pending**: Đang chờ đủ thời gian `for`
- **Firing**: Đã kích hoạt và đang gửi cảnh báo

### 2. Xem alerts trong Alertmanager

Truy cập: http://localhost:9093

Bạn sẽ thấy:
- Alerts đang **Firing**
- Lịch sử cảnh báo
- Cấu hình routing

### 3. Test Alert

Để test alert, bạn có thể:

**Cách 1: Dừng một service**
```bash
docker-compose stop order-service
```

Sau 1 phút, bạn sẽ nhận được cảnh báo "Order Service is down".

**Cách 2: Tạo lỗi trong service**
- Gửi nhiều request với lỗi 500
- Hoặc tăng độ trễ của service

## Cấu trúc Alert Rule

Mỗi alert rule có cấu trúc:

```yaml
- alert: AlertName
  expr: PromQL_Query  # Điều kiện kích hoạt
  for: 2m             # Thời gian chờ trước khi kích hoạt
  labels:
    severity: critical # Mức độ nghiêm trọng
  annotations:
    summary: "Mô tả ngắn"
    description: "Mô tả chi tiết"
```

## Thêm Alert Rule mới

Để thêm alert rule mới, chỉnh sửa file `config/alerts.yml`:

```yaml
groups:
  - name: demo_alerts
    interval: 30s
    rules:
      # Thêm rule mới ở đây
      - alert: MyNewAlert
        expr: some_metric > threshold
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Mô tả ngắn"
          description: "Mô tả chi tiết: {{ $value }}"
```

Sau đó khởi động lại Prometheus:

```bash
docker-compose restart prometheus
```

## Troubleshooting

### Alerts không kích hoạt

1. **Kiểm tra Prometheus có scrape metrics không**
   - Truy cập: http://localhost:9090/targets
   - Đảm bảo tất cả targets đều "UP"

2. **Kiểm tra Alert Rule syntax**
   - Truy cập: http://localhost:9090/rules
   - Xem có lỗi nào không

3. **Kiểm tra PromQL query**
   - Truy cập: http://localhost:9090/graph
   - Test query trong alert rule

### Email không được gửi

1. **Kiểm tra cấu hình SMTP**
   - Xem logs của Alertmanager: `docker-compose logs alertmanager`

2. **Kiểm tra App Password**
   - Đảm bảo đã copy đúng App Password (không có khoảng trắng)

3. **Kiểm tra firewall**
   - Đảm bảo port 587 không bị chặn

### Xem logs Alertmanager

```bash
docker-compose logs -f alertmanager
```

## Các kênh cảnh báo khác (tùy chọn)

Ngoài email, bạn có thể cấu hình:

- **Slack**: Thêm webhook URL vào receivers
- **PagerDuty**: Thêm integration key
- **Webhook**: Gửi HTTP POST request

Xem thêm tại: https://prometheus.io/docs/alerting/latest/configuration/

## Tài liệu tham khảo

- [Prometheus Alerting](https://prometheus.io/docs/alerting/latest/overview/)
- [Alertmanager Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)


