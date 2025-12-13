# 🚀 Error Scenario - End-to-End Testing

## Mục đích

Tạo một request đi qua tất cả services, inject error ở payment-service, trigger alert, và xem trace trong Grafana.

## Các bước

### 1. Restart Services với code mới

```bash
docker-compose restart order-service payment-service
```

Hoặc rebuild:

```bash
docker-compose up -d --build order-service payment-service
```

### 2. Chạy Test Luồng Thực Tế

```bash
python tests/test_real_flow.py
```

Script này sẽ:
- Tạo order request (như trong thực tế)
- Inject error vào payment service
- Hiển thị trace ID và link để xem trace trong Grafana
- Hiển thị vị trí log files
- Hiển thị link đến dashboard
- Trigger alert sau 10 giây
- Email sẽ được gửi với link Grafana

### 4. Kiểm tra Email

- Kiểm tra: `tuanhuy030799@gmail.com`
- Click vào nút "🔍 View Traces in Grafana" trong email
- Hoặc mở Grafana: http://localhost:3000/explore

### 5. Xem Trace trong Grafana

1. Mở Grafana: http://localhost:3000
2. Vào **Explore** → Chọn **Tempo**
3. Time range: **Last 15 minutes**
4. Xem traces và tìm error ở payment-service

## Flow

```
User Request (tests/test_real_flow.py)
    ↓
Order Service (POST /orders với inject_error=true)
    ↓
Inventory Service (GET /inventory/1)
    ↓
Payment Service (POST /payments với inject_error=true) ❌ ERROR
    ↓
Alert Triggered (sau 10s khi có error rate cao)
    ↓
Email Sent với link Grafana
    ↓
Click link → Grafana → View Trace
```

## Troubleshooting

### Error không được inject?

1. **Restart services:**
   ```bash
   docker-compose restart order-service payment-service
   ```

2. **Rebuild services:**
   ```bash
   docker-compose up -d --build order-service payment-service
   ```

3. **Kiểm tra logs:**
   ```bash
   docker-compose logs order-service
   docker-compose logs payment-service
   ```

### Alert không được gửi?

1. **Kiểm tra Prometheus alerts:**
   - http://localhost:9090/alerts

2. **Kiểm tra Alertmanager:**
   - http://localhost:9093

3. **Kiểm tra logs:**
   ```bash
   docker-compose logs alertmanager
   ```

### Không thấy trace trong Grafana?

1. **Kiểm tra Tempo:**
   - http://localhost:3200

2. **Kiểm tra Grafana datasource:**
   - Grafana → Configuration → Data Sources → Tempo

3. **Đợi vài giây** để trace được index

## Files

- `tests/test_real_flow.py` - Script chính để test luồng thực tế (Request → Error → Trace → Logs → Dashboard)
- `scripts/setup_and_test.bat` - Script tự động setup và test (Windows)
- `scripts/trigger_error_scenario.py` - Script cũ (deprecated, sử dụng test_real_flow.py thay thế)

