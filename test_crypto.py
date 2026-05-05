from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64

def derive_key(password: str, salt: bytes) -> bytes:
    """Turn a password into a 256-bit AES key"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(password.encode())

def encrypt(data: bytes, password: str) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, data, None)
    return salt + nonce + encrypted

def decrypt(data: bytes, password: str) -> bytes:
    salt = data[:16]
    nonce = data[16:28]
    encrypted = data[28:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, encrypted, None)

# ── Test ─────────────────────────────────────────────
password = "testpassword123"
original = b"Hello, this is a secret message!"

print(f"Original:  {original}")

encrypted = encrypt(original, password)
print(f"Encrypted: {encrypted[:30]}... ({len(encrypted)} bytes)")

decrypted = decrypt(encrypted, password)
print(f"Decrypted: {decrypted}")

print(f"\nMatch: {original == decrypted} ✅" if original == decrypted else "\nMismatch ❌")

# Test wrong password
try:
    decrypt(encrypted, "wrongpassword")
    print("Wrong password accepted ❌")
except Exception:
    print("Wrong password rejected ✅")