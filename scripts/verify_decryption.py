import json
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def decrypt_data(encrypted_dict, password):
    key = hashlib.sha256(password.encode()).digest()
    iv = base64.b64encode(base64.b64decode(encrypted_dict['iv'])).decode() # Just checking format
    iv_bytes = base64.b64decode(encrypted_dict['iv'])
    ciphertext = base64.b64decode(encrypted_dict['ciphertext'])
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv_bytes), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    return json.loads(data.decode('utf-8'))

def main():
    with open('re-archive/assets/data/stats.json', 'r') as f:
        encrypted = json.load(f)
    
    try:
        decrypted = decrypt_data(encrypted, "72941")
        print("Top-level keys:", decrypted.keys())
        print("Total sub-keys:", decrypted['total'].keys())
        print("Dong stats in Total:", 'dong_stats' in decrypted['total'])
        print("Sample Dong Data:", decrypted['total']['dong_stats'][0] if decrypted['total'].get('dong_stats') else "None")
        print("Generated at:", decrypted.get('generated_at'))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
