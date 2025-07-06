# 📡 Ứng dụng bảo mật tin nhắn văn bản với DES và RSA

## 🚀 Giới thiệu

Đây là **bài tập lớn môn An toàn và Bảo mật thông tin - Đề 18**, xây dựng hệ thống **ứng dụng chat bảo mật tin nhắn văn bản** nhằm đảm bảo:

✅ **Bảo mật nội dung tin nhắn** bằng DES (CFB).  
✅ **Xác thực danh tính** người gửi bằng RSA 2048-bit (OAEP + SHA-256).  
✅ **Đảm bảo toàn vẹn dữ liệu** qua SHA-256.  
✅ Giúp sinh viên hiểu cách ứng dụng mã hóa, chữ ký số, kiểm tra toàn vẹn trong thực tế.

---

## 🛠️ Trình bày kỹ thuật

### 1️⃣ Công nghệ sử dụng

- **Ngôn ngữ:** Python
- **Thư viện:** `socket`, `pycryptodome`, `hashlib`
- **Mô hình:** Client-Server / P2P

### 2️⃣ Các thuật toán triển khai

- **DES (CFB):** Mã hóa/giải mã tin nhắn, tránh bị đọc lén.
- **RSA 2048-bit:** Trao đổi khóa DES, ký số xác thực danh tính người gửi.
- **SHA-256:** Tạo hash kiểm tra tính toàn vẹn tin nhắn.

### 3️⃣ Quy trình hoạt động

1️⃣ **Handshake:** Client gửi "Hello!", server trả lời "Ready!", trao đổi public key RSA.  
2️⃣ **Xác thực & trao khóa:** Client ký ID, mã hóa khóa DES bằng RSA gửi cho server.  
3️⃣ **Mã hóa & gửi:** Client mã hóa tin nhắn bằng DES, tạo hash SHA-256, gửi kèm chữ ký RSA.  
4️⃣ **Nhận & giải mã:** Server kiểm tra hash, xác thực chữ ký, giải mã hiển thị tin nhắn.

---

## 🖥️ Hình ảnh minh họa

### ⚡ Sơ đồ hệ thống

![Sơ đồ bảo mật tin nhắn](link_anh_so_do)

### ⚡ Giao diện terminal

![Giao diện gửi]()
![Giao diện nhận]()

---

## 💻 Hướng dẫn chạy

1️⃣ Cài thư viện:
```bash
pip install pycryptodome
```

2️⃣ Chạy server:
```bash
python server.py
```

3️⃣ Chạy client:
```bash
python client.py
```

4️⃣ Nhập tin nhắn cần gửi, quan sát kết quả mã hóa, hash, chữ ký và nội dung nhận.

---

## 🌱 Hướng phát triển

✅ Nâng cấp AES thay DES để tăng bảo mật.  
✅ Xây dựng giao diện GUI Tkinter.  
✅ Lưu lịch sử tin nhắn.  
✅ Mở rộng gửi file hoặc voice chat bảo mật.

---

## 🪪 Tác giả

- **Họ tên:** Nguyễn Thị Thùy Linh
- **Lớp:** CNTT16-05
- **Môn:** An toàn và Bảo mật thông tin
- **GVHD:** Trần Đức Thắng


