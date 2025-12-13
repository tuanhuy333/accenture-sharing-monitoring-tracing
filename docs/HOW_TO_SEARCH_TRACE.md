# 🔍 Hướng dẫn Search Trace trong Grafana Tempo

## Cách 1: Search bằng Trace ID

1. Trong ô **"Enter a TraceQL query or trace ID"**
2. Nhập trace ID (ví dụ: `78e4efea75a4dd7b7600bef67acd165b`)
3. Nhấn **Shift+Enter** hoặc click **Run query**

## Cách 2: Search bằng TraceQL Query

### Tìm traces có error:
```
{ status = "error" }
```

### Tìm traces của một service:
```
{ service.name = "payment-service" }
```

### Tìm traces có error trong payment-service:
```
{ service.name = "payment-service" && status = "error" }
```

### Tìm traces trong khoảng thời gian gần đây:
```
{ service.name = "order-service" } | limit 20
```

## Cách 3: Search bằng Service Name

1. Click vào tab **"Search"** (thay vì TraceQL)
2. Chọn **Service**: `payment-service` hoặc `order-service`
3. Chọn **Operation**: `process_payment` hoặc `create_order`
4. Chọn **Time range**: Last 15 minutes
5. Click **Run query**

## Cách 4: Tìm traces có error

1. Ở tab **"Search"**
2. Chọn **Service**: `payment-service`
3. Chọn **Tags**: `status=error` hoặc `error=true`
4. Click **Run query**

## Trace ID từ test vừa rồi:

```
78e4efea75a4dd7b7600bef67acd165b
```

Paste trace ID này vào ô query và nhấn Shift+Enter để xem trace chi tiết!

