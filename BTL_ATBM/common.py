from Crypto.Cipher import DES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
import json

def encrypt_message(message, des_key, iv):
    if not message or not des_key or not iv:
        raise ValueError("Dữ liệu đầu vào không hợp lệ cho mã hóa")
    cipher = DES.new(des_key, DES.MODE_CFB, iv=iv)
    return cipher.encrypt(message.encode())

def decrypt_message(ciphertext, des_key, iv):
    if not ciphertext or not des_key or not iv:
        raise ValueError("Dữ liệu đầu vào không hợp lệ cho giải mã")
    cipher = DES.new(des_key, DES.MODE_CFB, iv=iv)
    return cipher.decrypt(ciphertext).decode().rstrip()

def create_packet(message, sender_private_key, receiver_public_key, sender_id):
    if not message or not sender_private_key or not receiver_public_key or not sender_id:
        raise ValueError("Dữ liệu đầu vào không đầy đủ để tạo gói tin")
    des_key = get_random_bytes(8)
    iv = get_random_bytes(8)
    ciphertext = encrypt_message(message, des_key, iv)
    hash_val = SHA256.new(ciphertext)
    sig_info = SHA256.new(sender_id.encode())
    signature = pkcs1_15.new(sender_private_key).sign(sig_info)
    encrypted_key = PKCS1_OAEP.new(receiver_public_key).encrypt(des_key)
    packet = {
        "iv": b64encode(iv).decode(),
        "cipher": b64encode(ciphertext).decode(),
        "hash": hash_val.hexdigest(),
        "sig": b64encode(signature).decode(),
        "encrypted_des_key": b64encode(encrypted_key).decode(),
        "signed_info": b64encode(sig_info.digest()).decode(),
        "sender_id": sender_id,
        "sender_pub": sender_private_key.publickey().export_key().decode()  # Đã fix
    }
    return json.dumps(packet)

def parse_and_decrypt(packet_json, sender_public_key, receiver_private_key):
    if not packet_json or not sender_public_key or not receiver_private_key:
        return "[ERROR] Dữ liệu đầu vào không hợp lệ"
    try:
        packet = json.loads(packet_json)
        if not all(key in packet for key in ["iv", "cipher", "hash", "sig", "encrypted_des_key", "signed_info", "sender_id", "sender_pub"]):
            return "[ERROR] Gói tin thiếu trường bắt buộc"
        iv = b64decode(packet["iv"])
        cipher = b64decode(packet["cipher"])
        hash_recv = packet["hash"]
        signature = b64decode(packet["sig"])
        enc_key = b64decode(packet["encrypted_des_key"])
        sender_id = packet["sender_id"]
        signed_info = b64decode(packet["signed_info"])
        des_key = PKCS1_OAEP.new(receiver_private_key).decrypt(enc_key)
        hash_check = SHA256.new(cipher)
        if hash_check.hexdigest() != hash_recv:
            return "[ERROR] Hash mismatch"
        sig_info = SHA256.new(sender_id.encode())
        if sig_info.digest() != signed_info:
            return "[ERROR] Signed info mismatch"
        pkcs1_15.new(sender_public_key).verify(sig_info, signature)
        return decrypt_message(cipher, des_key, iv)
    except (json.JSONDecodeError, KeyError, ValueError, binascii.Error) as e:
        return f"[ERROR] Giải mã thất bại: {e}"