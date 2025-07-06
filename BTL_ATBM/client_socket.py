import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket, json
from Crypto.PublicKey import RSA
from Crypto.Cipher import DES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from base64 import b64encode
from binascii import hexlify

try:
    sender_key = RSA.import_key(open('sender_private.pem', 'rb').read())
except FileNotFoundError:
    raise FileNotFoundError("Không tìm thấy sender_private.pem. Hãy chạy generate_keys_socket.py trước.")

receiver_public = None
HOST = '127.0.0.1'
PORT = 65432

root = tk.Tk()
root.title("Ứng Dụng Gửi Tin Nhắn - Sender")
root.geometry("600x750")
root.resizable(False, False)

main_frame = tk.Frame(root, padx=20, pady=10)
main_frame.pack(fill='both', expand=True)

status_label = tk.Label(root, text="Sẵn sàng", fg="blue")
status_label.pack(pady=5)

# Global
current_des_key_bytes = None

def generate_des_key():
    global current_des_key_bytes
    des_key = get_random_bytes(8)
    current_des_key_bytes = des_key
    des_key_display.config(state='normal')
    des_key_display.delete(0, tk.END)
    des_key_display.insert(0, hexlify(des_key).decode())
    des_key_display.config(state='readonly')

def perform_handshake():
    global receiver_public
    try:
        print("[CLIENT] Kết nối tới server...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.sendall(b"Hello!")
        response = s.recv(1024).decode('utf-8').strip()
        print(f"[CLIENT] Nhận phản hồi: {response}")

        if response != "Ready!":
            raise ValueError(f"Handshake thất bại. Phản hồi không hợp lệ: {response}")

        s.sendall(sender_key.publickey().export_key())
        receiver_pub_pem = s.recv(4096).decode('utf-8').strip()
        if not receiver_pub_pem:
            raise ValueError("Không nhận được khóa công khai từ máy chủ")

        receiver_public = RSA.import_key(receiver_pub_pem)
        receiver_public_key_display.config(state='normal')
        receiver_public_key_display.delete("1.0", tk.END)
        receiver_public_key_display.insert("1.0", receiver_pub_pem)
        receiver_public_key_display.config(state='disabled')
        status_label.config(text="✅ Handshake thành công!", fg="green")
        s.close()

    except Exception as e:
        print(f"[CLIENT] ❌ Lỗi handshake: {e}")
        status_label.config(text=f"❌ Lỗi handshake: {e}", fg="red")
        messagebox.showerror("Handshake Lỗi", f"Lỗi khi kết nối: {e}")

def encrypt_and_sign_and_send():
    global current_des_key_bytes, receiver_public
    msg = message_input.get("1.0", tk.END).strip()
    sender_id = sender_id_input.get().strip()
    if not msg or not sender_id or not current_des_key_bytes or not receiver_public:
        messagebox.showwarning("Thiếu", "Điền đủ ID, tin nhắn, tạo DES và handshake trước đã!")
        return
    try:
        iv = get_random_bytes(8)
        cipher = DES.new(current_des_key_bytes, DES.MODE_CFB, iv)
        ciphertext = cipher.encrypt(msg.encode())

        rsa_cipher = PKCS1_OAEP.new(receiver_public)
        encrypted_des_key = rsa_cipher.encrypt(current_des_key_bytes)

        h = SHA256.new(sender_id.encode())
        signature = pkcs1_15.new(sender_key).sign(h)

        packet = {
            "iv": b64encode(iv).decode(),
            "cipher": b64encode(ciphertext).decode(),
            "hash": SHA256.new(ciphertext).hexdigest(),
            "sig": b64encode(signature).decode(),
            "encrypted_des_key": b64encode(encrypted_des_key).decode(),
            "signed_info": b64encode(h.digest()).decode(),
            "sender_id": sender_id,
            "sender_pub": sender_key.publickey().export_key().decode()
        }

        packet_json = json.dumps(packet)

        encrypted_message_output.config(state='normal')
        encrypted_message_output.delete("1.0", tk.END)
        encrypted_message_output.insert("1.0", packet['cipher'])
        encrypted_message_output.config(state='disabled')

        signature_output.config(state='normal')
        signature_output.delete("1.0", tk.END)
        signature_output.insert("1.0", packet['sig'])
        signature_output.config(state='disabled')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.sendall(packet_json.encode('utf-8'))
        response = s.recv(1024).decode('utf-8').strip()
        s.close()

        ack_nack_output.config(state='normal')
        ack_nack_output.delete("1.0", tk.END)
        ack_nack_output.insert("1.0", response)
        ack_nack_output.config(state='disabled')
        status_label.config(text=f"✅ Phản hồi từ server: {response}", fg="green")
    except Exception as e:
        print(f"[CLIENT] ❌ Lỗi gửi: {e}")
        status_label.config(text=f"❌ Gửi lỗi: {e}", fg="red")
        messagebox.showerror("Gửi lỗi", str(e))

# GUI

tk.Label(main_frame, text="ID người gửi:").pack(anchor='w')
sender_id_input = tk.Entry(main_frame)
sender_id_input.pack(fill='x')

tk.Label(main_frame, text="Khóa DES:").pack(anchor='w')
des_key_display = tk.Entry(main_frame, state='readonly')
des_key_display.pack(fill='x')

generate_des_key()

tk.Label(main_frame, text="Tin nhắn:").pack(anchor='w')
message_input = scrolledtext.ScrolledText(main_frame, height=5)
message_input.pack(fill='x')

handshake_button = tk.Button(main_frame, text="Thực hiện Handshake", command=perform_handshake,
                             bg="orange", fg="white", font=("Helvetica", 12, "bold"))
handshake_button.pack(fill='x', pady=5)

tk.Label(main_frame, text="Tin nhắn mã hóa:").pack(anchor='w')
encrypted_message_output = scrolledtext.ScrolledText(main_frame, height=4, state='disabled')
encrypted_message_output.pack(fill='x')

tk.Label(main_frame, text="Chữ ký số:").pack(anchor='w')
signature_output = scrolledtext.ScrolledText(main_frame, height=3, state='disabled')
signature_output.pack(fill='x')

tk.Label(main_frame, text="Khóa công khai người nhận:").pack(anchor='w')
receiver_public_key_display = scrolledtext.ScrolledText(main_frame, height=5, state='disabled')
receiver_public_key_display.pack(fill='x')

tk.Label(main_frame, text="Phản hồi từ server:").pack(anchor='w')
ack_nack_output = scrolledtext.ScrolledText(main_frame, height=3, state='disabled')
ack_nack_output.pack(fill='x')

tk.Button(main_frame, text="Mã hóa, Ký & Gửi", command=encrypt_and_sign_and_send,
          bg="blue", fg="white", font=("Helvetica", 12, "bold")).pack(fill='x', pady=10)

root.mainloop()