# 🔧 Hướng dẫn Sửa Lỗi Email Cảnh báo

## ❌ Vấn đề hiện tại:

1. **Lỗi xác thực**: "Username and Password not accepted"
   - Bạn đang dùng mật khẩu Gmail thông thường thay vì **App Password**

2. **Lỗi cú pháp YAML**: Đã được sửa tự động

## ✅ Giải pháp:

### Bước 1: Tạo App Password cho Gmail

1. **Bật 2-Factor Authentication (2FA)**
   - Vào: https://myaccount.google.com/security
   - Bật "2-Step Verification" nếu chưa bật

2. **Tạo App Password**
   - Vào: https://myaccount.google.com/apppasswords
   - Chọn "Mail" → "Other (Custom name)"
   - Nhập tên: `Alertmanager`
   - Click "Generate"
   - **Copy mật khẩu 16 ký tự** (ví dụ: `abcd efgh ijkl mnop`)

### Bước 2: Cập nhật file `config/alertmanager.yml`

Mở file `config/alertmanager.yml` và thay đổi:

```yaml
global:
  smtp_auth_password: 'YOUR-16-CHAR-APP-PASSWORD'  # Thay bằng App Password 16 ký tự
```

**Lưu ý quan trọng:**
- ❌ KHÔNG dùng mật khẩu Gmail thông thường
- ✅ PHẢI dùng App Password (16 ký tự, có thể có khoảng trắng)
- Nếu App Password có khoảng trắng, có thể bỏ khoảng trắng hoặc giữ nguyên

### Bước 3: Khởi động lại Alertmanager

```bash
docker-compose restart alertmanager
```

### Bước 4: Kiểm tra logs

```bash
docker-compose logs -f alertmanager
```

Nếu thành công, bạn sẽ thấy:
- ✅ Không còn lỗi "Username and Password not accepted"
- ✅ Có thể thấy "Successfully sent notification"

### Bước 5: Test Alert

Để test alert và nhận email:

```bash
# Dừng một service để trigger alert
docker-compose stop order-service

# Đợi 1 phút, sau đó kiểm tra email
```

## 🔍 Kiểm tra cấu hình hiện tại

Xem file `config/alertmanager.yml`:
- `smtp_from`: Email gửi (phải là Gmail của bạn)
- `smtp_auth_username`: Email đăng nhập (giống smtp_from)
- `smtp_auth_password`: **PHẢI là App Password**
- `to`: Email nhận cảnh báo

## ⚠️ Troubleshooting

### Vẫn không nhận được email?

1. **Kiểm tra logs Alertmanager:**
   ```bash
   docker-compose logs alertmanager | grep -i error
   ```

2. **Kiểm tra có alerts đang firing không:**
   - Vào: http://localhost:9090/alerts
   - Xem có alerts nào ở trạng thái "Firing" không

3. **Kiểm tra Alertmanager:**
   - Vào: http://localhost:9093
   - Xem có alerts nào không

4. **Kiểm tra App Password:**
   - Đảm bảo đã copy đúng 16 ký tự
   - Không có ký tự đặc biệt không hợp lệ

5. **Thử tạo App Password mới:**
   - Xóa App Password cũ
   - Tạo App Password mới
   - Cập nhật lại trong file config

## 📧 Các email provider khác

Nếu không dùng Gmail, bạn có thể dùng:

### Outlook/Hotmail:
```yaml
smtp_smarthost: 'smtp-mail.outlook.com:587'
```

### Yahoo:
```yaml
smtp_smarthost: 'smtp.mail.yahoo.com:587'
```

### SMTP Server riêng:
```yaml
smtp_smarthost: 'smtp.yourdomain.com:587'
smtp_auth_username: 'your-email@yourdomain.com'
smtp_auth_password: 'your-password'
```


