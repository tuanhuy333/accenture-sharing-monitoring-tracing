# Hướng dẫn Nhanh: Thiết lập Cảnh báo

## 🚀 Bước 1: Cấu hình Email (Bắt buộc)

### Nếu dùng Gmail:

1. **Bật 2FA cho Gmail**
   - Vào: https://myaccount.google.com/security
   - Bật "2-Step Verification"

2. **Tạo App Password**
   - Vào: https://myaccount.google.com/apppasswords
   - Chọn "Mail" → "Other" → Nhập tên "Alertmanager"
   - Copy mật khẩu 16 ký tự

3. **Cập nhật `config/alertmanager.yml`**
   ```yaml
   global:
     smtp_from: 'your-email@gmail.com'
     smtp_auth_username: 'your-email@gmail.com'
     smtp_auth_password: 'your-16-char-password'
   
   receivers:
     - name: 'email-notifications'
       email_configs:
         - to: 'your-recipient-email@gmail.com'  # Email nhận cảnh báo
   ```

4. **Khởi động lại Alertmanager**
   ```bash
   docker-compose restart alertmanager
   ```

## ✅ Bước 2: Kiểm tra Alerts

### Xem alerts trong Prometheus:
- URL: http://localhost:9090/alerts
- Xem trạng thái: Inactive, Pending, Firing

### Xem alerts trong Alertmanager:
- URL: http://localhost:9093
- Xem alerts đang firing và lịch sử

### Chạy script test:
```bash
python test_alerts.py
```

## 🧪 Bước 3: Test Alert

### Cách 1: Dừng một service
```bash
docker-compose stop order-service
```
Sau 1 phút sẽ nhận được cảnh báo "Order Service is down"

### Cách 2: Tạo nhiều lỗi
```bash
python test_alerts.py
# Chọn option 1 để test High Error Rate
```

## 📋 Các Alert Rules hiện có

1. **Service Down** - Cảnh báo khi service không phản hồi
2. **High Error Rate** - Cảnh báo khi tỷ lệ lỗi 5xx > 0.1/giây
3. **High Latency** - Cảnh báo khi độ trễ 95th percentile > 1 giây

## 🔧 Troubleshooting

### Alerts không kích hoạt?
1. Kiểm tra Prometheus: http://localhost:9090/targets
2. Kiểm tra rules: http://localhost:9090/rules
3. Xem logs: `docker-compose logs prometheus`

### Email không được gửi?
1. Kiểm tra logs: `docker-compose logs alertmanager`
2. Kiểm tra App Password đã đúng chưa
3. Kiểm tra firewall port 587

## 📚 Tài liệu chi tiết

Xem file `ALERTS_GUIDE.md` để biết thêm chi tiết.


