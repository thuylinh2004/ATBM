from Crypto.PublicKey import RSA

# Tạo cặp khóa RSA 2048-bit cho người gửi
sender_key = RSA.generate(2048)
with open('sender_private.pem', 'wb') as f:
    f.write(sender_key.export_key('PEM'))
with open('sender_public.pem', 'wb') as f:
    f.write(sender_key.publickey().export_key('PEM'))

# Tạo cặp khóa RSA 2048-bit cho người nhận
receiver_key = RSA.generate(2048)
with open('receiver_private.pem', 'wb') as f:
    f.write(receiver_key.export_key('PEM'))
with open('receiver_public.pem', 'wb') as f:
    f.write(receiver_key.publickey().export_key('PEM'))

print("✅ Đã tạo xong 4 file khóa RSA (PEM)")