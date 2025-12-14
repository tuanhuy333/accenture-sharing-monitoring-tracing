# Hướng Dẫn Xem Logs

## 📋 Tổng Quan

Hệ thống này sử dụng **Loki** để thu thập và lưu trữ logs từ tất cả các microservices. Logs được thu thập bởi **Promtail** và hiển thị trong **Grafana**.

## 🔍 Các Cách Xem Logs

### 1. **Grafana (Khuyến nghị - Cách tốt nhất)**

#### Truy cập Grafana:
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin`

#### Các bước xem logs:

1. **Vào Explore:**
   - Click vào biểu tượng **"Explore"** (🔍) ở sidebar bên trái
   - Hoặc truy cập trực tiếp: http://localhost:3000/explore

2. **Chọn datasource Loki:**
   - Ở dropdown phía trên, chọn **"Loki"**

3. **Nhập query để xem logs:**

   **Xem tất cả logs:**
   ```
   {job=~".*-service"}
   ```

   **Xem logs của một service cụ thể:**
   ```
   {service="user-service"}
   ```
   hoặc
   ```
   {job="user-service"}
   ```

   **Xem logs có chứa từ khóa:**
   ```
   {job=~".*-service"} |= "error"
   ```
   hoặc
   ```
   {service="order-service"} |= "Failed"
   ```

   **Xem logs của nhiều services:**
   ```
   {job=~"user-service|order-service|payment-service"}
   ```

   **Tìm logs theo trace ID:**
   ```
   {job=~".*-service"} |= "trace_id_here"
   ```

4. **Chọn thời gian:**
   - Ở góc trên bên phải, chọn time range (ví dụ: Last 15 minutes, Last 1 hour, v.v.)

5. **Xem kết quả:**
   - Logs sẽ hiển thị dưới dạng bảng với timestamp, labels, và message
   - Click vào một log entry để xem chi tiết

#### Ví dụ Query phổ biến:

```logql
# Tất cả logs trong 1 giờ qua
{job=~".*-service"}

# Logs có lỗi
{job=~".*-service"} |= "error" or {job=~".*-service"} |= "Error" or {job=~".*-service"} |= "ERROR"

# Logs của user-service có chứa "user"
{service="user-service"} |= "user"

# Logs theo level
{job=~".*-service"} | json | level="ERROR"

# Logs của order flow
{service="order-service"} or {service="payment-service"} or {service="inventory-service"}
```

### 2. **Loki API Trực Tiếp**

#### Truy cập Loki UI:
- URL: http://localhost:3100
- Đây là giao diện đơn giản của Loki

#### Sử dụng API:

**Xem danh sách labels:**
```bash
curl http://localhost:3100/loki/api/v1/labels
```

**Query logs (PowerShell):**
```powershell
# Xem logs của user-service
Invoke-WebRequest -Uri "http://localhost:3100/loki/api/v1/query_range?query={job=`"user-service`"}&limit=100" | Select-Object -ExpandProperty Content
```

**Query logs với thời gian:**
```powershell
$start = [DateTimeOffset]::Now.AddHours(-1).ToUnixTimeSeconds()
$end = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$query = "{job=`"user-service`"}"
$url = "http://localhost:3100/loki/api/v1/query_range?query=$query&start=${start}000000000&end=${end}000000000&limit=100"
Invoke-WebRequest -Uri $url | Select-Object -ExpandProperty Content
```

### 3. **Docker Logs**

#### Xem logs của containers:

**Xem logs của một service:**
```bash
docker logs user-service
docker logs order-service
docker logs payment-service
```

**Xem logs real-time (follow):**
```bash
docker logs -f user-service
docker logs -f promtail
docker logs -f loki
```

**Xem logs của tất cả services:**
```bash
docker-compose logs -f
```

**Xem logs của monitoring stack:**
```bash
docker logs promtail
docker logs loki
docker logs grafana
```

**Xem logs với giới hạn số dòng:**
```bash
docker logs --tail 100 user-service
docker logs --tail 50 -f promtail
```

### 4. **Log Files Trên Host**

#### Vị trí thư mục logs:
```
c:\Users\Tuan Huy\Desktop\sharing-monitoring-tracing\logs\
```

#### Các file logs:
- `user-service.log`
- `order-service.log`
- `payment-service.log`
- `inventory-service.log`
- `shipping-service.log`
- `notification-service.log`
- `review-service.log`
- `auth-service.log`

#### Xem logs bằng PowerShell:
```powershell
# Xem toàn bộ file
Get-Content .\logs\user-service.log

# Xem real-time (tail)
Get-Content .\logs\user-service.log -Wait -Tail 50

# Tìm kiếm trong logs
Select-String -Path .\logs\*.log -Pattern "error" -CaseSensitive:$false

# Xem logs của nhiều services
Get-Content .\logs\user-service.log, .\logs\order-service.log -Tail 20
```

## 🔧 Troubleshooting

### Không thấy logs trong Grafana?

1. **Kiểm tra Promtail có chạy không:**
   ```bash
   docker ps | findstr promtail
   docker logs promtail
   ```

2. **Kiểm tra Loki có chạy không:**
   ```bash
   docker ps | findstr loki
   docker logs loki
   ```

3. **Kiểm tra log files có tồn tại không:**
   ```powershell
   dir .\logs\
   ```

4. **Kiểm tra Promtail có đọc được files không:**
   ```bash
   docker logs promtail | findstr "error"
   ```

5. **Restart các services:**
   ```bash
   docker-compose restart promtail loki
   ```

### Logs không được thu thập?

1. **Kiểm tra volume mount:**
   - Promtail cần mount: `./logs:/var/log/app:ro`
   - Services cần mount: `./logs:/app/logs`

2. **Kiểm tra quyền truy cập:**
   - Đảm bảo thư mục `logs` tồn tại và có quyền đọc

3. **Kiểm tra format logs:**
   - Logs phải được ghi vào đúng path: `/app/logs/<service-name>.log`

## 📊 Dashboard Logs

Bạn cũng có thể xem logs trong các Grafana Dashboards:
- Vào **Dashboards** → Chọn dashboard có sẵn
- Nhiều dashboards có panels hiển thị logs tích hợp

## 💡 Tips

1. **Sử dụng LogQL trong Grafana:**
   - LogQL là ngôn ngữ query mạnh mẽ của Loki
   - Học thêm tại: https://grafana.com/docs/loki/latest/logql/

2. **Tạo Dashboard tùy chỉnh:**
   - Tạo dashboard mới trong Grafana
   - Thêm panel với query LogQL
   - Lưu để sử dụng lại

3. **Alerting từ logs:**
   - Có thể tạo alerts dựa trên log patterns
   - Ví dụ: alert khi có quá nhiều error logs

4. **Tích hợp với Traces:**
   - Trong Tempo (tracing), click vào span để xem logs liên quan
   - Logs được link với traces qua trace ID

## 🔗 Liên Kết Hữu Ích

- Grafana: http://localhost:3000
- Loki: http://localhost:3100
- Prometheus: http://localhost:9090
- Tempo: http://localhost:3200

