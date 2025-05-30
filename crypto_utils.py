from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from key import KEY

def pad(data):
    pad_len = AES.block_size - len(data) % AES.block_size
    return data + bytes([pad_len] * pad_len)

def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def encrypt_audio(data: bytes) -> bytes:
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data))
    return iv + encrypted

def decrypt_audio(encrypted_audio: bytes) -> bytes:
    iv = encrypted_audio[:16]
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_audio[16:])
    return unpad(decrypted)