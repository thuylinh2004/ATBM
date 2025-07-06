import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket, threading, json
from Crypto.PublicKey import RSA
from Crypto.Cipher import DES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from base64 import b64decode

try:
    receiver_key = RSA.import_key(open('receiver_private.pem', 'rb').read())
    receiver_public = receiver_key.publickey()
except FileNotFoundError:
    raise FileNotFoundError("Không tìm thấy receiver_private.pem. Hãy chạy generate_keys_socket.py trước.")

HOST = '127.0.0.1'
PORT = 65432

root = tk.Tk()
root.title("Ứng Dụng Nhận Tin Nhắn - Receiver")
root.geometry("600x750")
root.resizable(False, False)

header_frame = tk.Frame(root, pady=10)
header_frame.pack(fill='x')
tk.Label(header_frame, text="NHẬN TIN NHẮN BẢO MẬT", font=("Helvetica", 16, "bold")).pack()
tk.Label(header_frame, text="DES-CFB & Xác thực RSA 2048", font=("Helvetica", 10)).pack()

main_frame = tk.Frame(root, padx=20, pady=10)
main_frame.pack(fill='both', expand=True)

status_label = tk.Label(root, text="⏳ Đang khởi động server...", fg="blue")
status_label.pack(pady=5)

# === CÁC TRƯỜNG HIỂN THỊ ===
label_cipher = tk.Label(main_frame, text="📦 Tin nhắn đã mã hóa (Base64):", font=("Helvetica", 10, "bold"), anchor='w')
label_cipher.pack(fill='x', pady=(5, 0))
cipher_text_input = scrolledtext.ScrolledText(main_frame, height=5, wrap=tk.WORD, state='disabled')
cipher_text_input.pack(fill='x', pady=(0, 10))

label_sig = tk.Label(main_frame, text="🖊️ Chữ ký số (Base64):", font=("Helvetica", 10, "bold"), anchor='w')
label_sig.pack(fill='x', pady=(5, 0))
signature_input = scrolledtext.ScrolledText(main_frame, height=3, wrap=tk.WORD, state='disabled')
signature_input.pack(fill='x', pady=(0, 10))

label_plain = tk.Label(main_frame, text="📨 Nội dung tin nhắn sau khi giải mã:", font=("Helvetica", 10, "bold"), anchor='w')
label_plain.pack(fill='x', pady=(5, 0))
decrypted_message_output = scrolledtext.ScrolledText(main_frame, height=5, wrap=tk.WORD, state='disabled')
decrypted_message_output.pack(fill='x', pady=(0, 10))

tk.Button(main_frame, text="🔓 Giải mã", command=lambda: decrypt_message(),
          bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold")).pack(fill='x', pady=5)

tk.Button(main_frame, text="✅ Xác thực chữ ký", command=lambda: verify_signature(),
          bg="#C62828", fg="white", font=("Helvetica", 12, "bold")).pack(fill='x', pady=5)

data_packet = {}

def decrypt_message():
    global data_packet
    try:
        ciphertext = b64decode(data_packet['cipher'])
        iv = b64decode(data_packet['iv'])
        encrypted_des_key = b64decode(data_packet['encrypted_des_key'])

        if SHA256.new(ciphertext).hexdigest() != data_packet['hash']:
            raise ValueError("Hash không khớp")

        rsa_cipher = PKCS1_OAEP.new(receiver_key)
        des_key = rsa_cipher.decrypt(encrypted_des_key)

        cipher_des = DES.new(des_key, DES.MODE_CFB, iv=iv)
        plaintext = cipher_des.decrypt(ciphertext).decode().strip()

        decrypted_message_output.config(state='normal')
        decrypted_message_output.delete("1.0", tk.END)
        decrypted_message_output.insert("1.0", plaintext)
        decrypted_message_output.config(state='disabled')
        status_label.config(text="✅ Đã giải mã tin nhắn", fg="green")
    except Exception as e:
        status_label.config(text=f"❌ Lỗi giải mã: {e}", fg="red")
        messagebox.showerror("Lỗi Giải mã", str(e))

def verify_signature():
    global data_packet
    try:
        sig = b64decode(data_packet['sig'])
        sender_pub = RSA.import_key(data_packet['sender_pub'].encode())
        sender_id = data_packet['sender_id']
        signed_info = b64decode(data_packet['signed_info'])

        h = SHA256.new(sender_id.encode())
        if h.digest() != signed_info:
            raise ValueError("Signed info không khớp")

        pkcs1_15.new(sender_pub).verify(h, sig)
        status_label.config(text="✅ Chữ ký hợp lệ", fg="green")
        messagebox.showinfo("Xác thực", "Chữ ký hợp lệ. Tin nhắn đến từ người gửi được xác thực.")
    except Exception as e:
        status_label.config(text=f"❌ Chữ ký không hợp lệ: {e}", fg="red")
        messagebox.showerror("Lỗi Xác thực", str(e))

def update_gui_with_packet(packet):
    global data_packet
    data_packet = packet
    try:
        cipher = packet.get('cipher', '')
        sig = packet.get('sig', '')
        cipher_text_input.config(state='normal')
        cipher_text_input.delete("1.0", tk.END)
        cipher_text_input.insert("1.0", cipher)
        cipher_text_input.config(state='disabled')

        signature_input.config(state='normal')
        signature_input.delete("1.0", tk.END)
        signature_input.insert("1.0", sig)
        signature_input.config(state='disabled')

        decrypted_message_output.config(state='normal')
        decrypted_message_output.delete("1.0", tk.END)
        decrypted_message_output.insert("1.0", "")
        decrypted_message_output.config(state='disabled')

        status_label.config(text="✅ Đã nhận gói tin, chờ giải mã hoặc xác thực", fg="blue")
    except Exception as e:
        status_label.config(text=f"❌ Lỗi hiển thị: {e}", fg="red")

def socket_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"[SERVER] Đang lắng nghe tại {HOST}:{PORT}")
        root.after(0, status_label.config, {'text': f"✅ Máy chủ sẵn sàng tại {HOST}:{PORT}", 'fg': "green"})
        while True:
            try:
                conn, addr = s.accept()
                print(f"[SERVER] Kết nối từ: {addr}")
                data = conn.recv(1024).decode('utf-8').strip()
                if data == "Hello!":
                    conn.sendall(b"Ready!")  
                    sender_pub = conn.recv(4096).decode('utf-8').strip()
                    conn.sendall(receiver_public.export_key())
                else:
                    full_data = data + conn.recv(8192).decode('utf-8')
                    packet = json.loads(full_data)
                    root.after(0, update_gui_with_packet, packet)
                    conn.sendall("ACK: Đã nhận gói tin".encode('utf-8'))
                conn.close()
            except Exception as e:
                print(f"[SERVER] ❌ Lỗi khi xử lý gói tin: {e}")
    except Exception as e:
        print(f"[SERVER] ❌ Lỗi máy chủ: {e}")
        root.after(0, messagebox.showerror, "Lỗi máy chủ", str(e))

threading.Thread(target=socket_server, daemon=True).start()
root.mainloop()
