# Troubleshooting: Không Thấy Logs Trong Grafana

## ✅ Vấn Đề Đã Được Giải Quyết

Loki và Promtail đã được cấu hình đúng và đang hoạt động. Logs đã được thu thập và lưu trữ trong Loki.

## 🔍 Cách Kiểm Tra Logs Đang Hoạt Động

### 1. Thử Query Đơn Giản Trước

Trong Grafana Explore, thử các query sau:

**Xem tất cả logs:**
```
{job=~".*-service"}
```

**Xem logs của một service:**
```
{service="inventory-service"}
```

**Xem logs có chứa từ khóa:**
```
{service="inventory-service"} |= "INFO"
```

### 2. Kiểm Tra Time Range

- **Quan trọng**: Chọn time range phù hợp ở góc trên bên phải
- Nếu Promtail vừa restart, chỉ có logs từ sau thời điểm restart
- Thử: "Last 15 minutes" hoặc "Last 1 hour"

### 3. Vấn Đề Với Trace ID Query

Nếu bạn đang tìm một trace ID cụ thể:
```
{service="inventory-service"} |= "1a6964998f5d67511807f60aa255a495"
```

**Vấn đề có thể là:**
- Trace ID này không tồn tại trong logs
- Trace ID này nằm trong logs cũ (trước khi Promtail restart)
- Logs hiện tại chưa có trace ID (chỉ có metrics calls)

**Giải pháp:**
1. Tạo traffic mới để generate logs với trace ID
2. Mở rộng time range để tìm logs cũ hơn
3. Tìm trace ID thực tế từ Tempo traces

## 🚀 Tạo Traffic Mới Để Có Logs

### Cách 1: Sử dụng script có sẵn
```bash
python scripts/generate_traffic.py
```

### Cách 2: Gọi API trực tiếp
```powershell
# Tạo request đến inventory-service
Invoke-WebRequest -Uri "http://localhost:8003/health" -UseBasicParsing
Invoke-WebRequest -Uri "http://localhost:8003/inventory" -UseBasicParsing
```

### Cách 3: Sử dụng test script
```bash
python tests/test_real_flow.py
```

## 📊 Kiểm Tra Logs Đã Được Thu Thập

### Kiểm tra qua API:
```powershell
# Xem labels có sẵn
Invoke-WebRequest -Uri "http://localhost:3100/loki/api/v1/labels" -UseBasicParsing

# Query logs
$query = '{service="inventory-service"}'
$url = "http://localhost:3100/loki/api/v1/query_range?query=$query&limit=10"
Invoke-WebRequest -Uri $url -UseBasicParsing | Select-Object -ExpandProperty Content
```

### Kiểm tra Promtail:
```bash
docker logs promtail --tail 50
```

### Kiểm tra Loki:
```bash
docker logs loki --tail 50
```

## 🔧 Các Vấn Đề Thường Gặp

### 1. "No logs volume available"

**Nguyên nhân:**
- Time range không đúng (quá ngắn hoặc quá cũ)
- Query quá cụ thể (trace ID không tồn tại)
- Chưa có logs trong khoảng thời gian đó

**Giải pháp:**
- Thử query đơn giản hơn: `{job=~".*-service"}`
- Mở rộng time range: "Last 1 hour" hoặc "Last 24 hours"
- Tạo traffic mới để generate logs

### 2. Promtail không gửi logs đến Loki

**Kiểm tra:**
```bash
docker logs promtail | findstr "error"
```

**Nếu thấy lỗi kết nối:**
```bash
docker-compose restart promtail loki
```

### 3. Logs cũ không hiển thị

**Nguyên nhân:**
- Promtail chỉ đọc logs mới sau khi restart
- Logs cũ (trước khi restart) không được gửi đến Loki

**Giải pháp:**
- Logs cũ vẫn có trong file trên host: `.\logs\*.log`
- Để xem logs cũ, đọc trực tiếp từ file hoặc mở rộng time range và tạo traffic mới

## 💡 Best Practices

1. **Luôn thử query đơn giản trước:**
   ```
   {job=~".*-service"}
   ```

2. **Kiểm tra time range phù hợp:**
   - Nếu vừa restart services: "Last 15 minutes"
   - Nếu muốn xem logs cũ: "Last 24 hours"

3. **Tạo traffic trước khi query:**
   - Generate traffic để có logs mới
   - Sau đó mới query trong Grafana

4. **Sử dụng Label Browser:**
   - Click "Label browser" trong Grafana Explore
   - Xem các labels và values có sẵn
   - Chọn từ dropdown thay vì gõ tay

## 🔗 Liên Kết

- Grafana: http://localhost:3000
- Loki API: http://localhost:3100
- Promtail logs: `docker logs promtail`
- Log files: `.\logs\*.log`

