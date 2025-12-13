# 🚀 Hướng dẫn Khởi động Hệ thống Alerts

## ⚡ Cách 1: Khởi động TẤT CẢ (Khuyến nghị)

### Windows:
```bash
start.bat
```

### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

### Hoặc dùng docker-compose trực tiếp:
```bash
docker-compose up -d
```

## 🎯 Cách 2: Chỉ khởi động Services cần thiết cho Alerts

### Tối thiểu cần:
```bash
# 1. Prometheus (BẮT BUỘC - để đánh giá alert rules)
docker-compose up -d prometheus

# 2. Alertmanager (BẮT BUỘC - để gửi cảnh báo)
docker-compose up -d alertmanager

# 3. Ít nhất 1-2 services để có metrics (CẦN THIẾT)
docker-compose up -d order-service user-service
```

### Để test đầy đủ:
```bash
# Khởi động monitoring stack
docker-compose up -d prometheus alertmanager

# Khởi động các services chính
docker-compose up -d order-service user-service payment-service inventory-service
```

## ✅ Kiểm tra Services đã chạy

```bash
docker-compose ps
```

Hoặc kiểm tra từng service:

```bash
# Kiểm tra Prometheus
curl http://localhost:9090/-/healthy

# Kiểm tra Alertmanager  
curl http://localhost:9093/-/healthy

# Kiểm tra một service
curl http://localhost:8001/health
```

## 📊 Truy cập Web UI

Sau khi khởi động, truy cập:

- **Prometheus**: http://localhost:9090
  - Xem alerts: http://localhost:9090/alerts
  - Xem targets: http://localhost:9090/targets
  - Xem rules: http://localhost:9090/rules

- **Alertmanager**: http://localhost:9093
  - Xem alerts đang firing
  - Xem cấu hình routing

- **Grafana** (nếu đã khởi động): http://localhost:3000
  - User: `admin`
  - Password: `admin`

## 🔍 Kiểm tra Alerts hoạt động

### 1. Kiểm tra Prometheus có scrape metrics không:
- Vào: http://localhost:9090/targets
- Tất cả targets phải có trạng thái **UP** (màu xanh)

### 2. Kiểm tra Alert Rules:
- Vào: http://localhost:9090/rules
- Xem có lỗi syntax không

### 3. Kiểm tra Alerts:
- Vào: http://localhost:9090/alerts
- Xem trạng thái: Inactive, Pending, Firing

### 4. Test Alert:
```bash
# Dừng một service để test
docker-compose stop order-service

# Đợi 1 phút, sau đó kiểm tra:
# - http://localhost:9090/alerts (sẽ thấy "OrderServiceDown" firing)
# - http://localhost:9093 (sẽ thấy alert trong Alertmanager)
# - Email của bạn (nếu đã cấu hình)
```

## 🛑 Dừng Services

```bash
# Dừng tất cả
docker-compose down

# Dừng một service cụ thể
docker-compose stop order-service

# Dừng và xóa volumes (xóa dữ liệu)
docker-compose down -v
```

## 📝 Lưu ý

1. **Docker phải đang chạy** trước khi khởi động services
2. **Cấu hình email** trong `config/alertmanager.yml` trước khi test alerts
3. **Đợi 1-2 phút** sau khi khởi động để services khởi tạo xong
4. **Kiểm tra logs** nếu có vấn đề:
   ```bash
   docker-compose logs prometheus
   docker-compose logs alertmanager
   ```

## 🐛 Troubleshooting

### Services không khởi động?
```bash
# Xem logs
docker-compose logs

# Xem logs của service cụ thể
docker-compose logs prometheus
docker-compose logs alertmanager
```

### Port đã được sử dụng?
```bash
# Kiểm tra port nào đang dùng
netstat -ano | findstr :9090  # Windows
lsof -i :9090                 # Linux/Mac

# Hoặc đổi port trong docker-compose.yml
```

### Prometheus không scrape được metrics?
- Kiểm tra services có đang chạy không: `docker-compose ps`
- Kiểm tra network: `docker network ls`
- Kiểm tra targets: http://localhost:9090/targets


