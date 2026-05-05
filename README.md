# 🔐 File Encryptor

A desktop application for encrypting and decrypting files using AES-256, built with Python.

---

## How It Works

| File | Content |
|------|---------|
| `hello.txt` (original) | `hello` |
| `hello.txt.enc` (encrypted) | `DC1 sG NAK e K SOH DC4 E y SYN VT zF...` |
| `hello.txt.decrypted` (decrypted) | `hello` |

The original file is completely unreadable once encrypted. Only the correct password can restore it.

---

## Features

- **AES-256-GCM Encryption** — Military-grade encryption standard used by governments and financial institutions
- **Password-Based Key Derivation** — Uses PBKDF2-SHA256 with 100,000 iterations to generate a secure key from your password
- **Random Salt & Nonce** — Every encryption is unique even with the same password and file
- **Tamper Detection** — GCM mode detects if an encrypted file has been modified or corrupted
- **Wrong Password Rejection** — Incorrect passwords are immediately detected and rejected
- **Encrypt Any File** — Works on text files, images, documents, and more
- **Activity Log** — Tracks encryption and decryption actions in the current session
- **Show/Hide Password** — Toggle password visibility while typing
- **Clean Dark UI** — Built with Tkinter and a modern dark theme

---

## Tech Stack

- **Python 3.10**
- **Cryptography** — AES-256-GCM encryption, PBKDF2HMAC key derivation
- **Tkinter** — GUI framework
- **Threading** — Non-blocking encryption/decryption operations

---

## Encryption Details

| Property | Value |
|----------|-------|
| Algorithm | AES-256-GCM |
| Key Size | 256 bits |
| Key Derivation | PBKDF2-SHA256 |
| Iterations | 100,000 |
| Salt | 16 bytes (random per file) |
| Nonce | 12 bytes (random per file) |

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MaxsCaretaker/file-encryptor.git
   cd file-encryptor
   ```

2. Install dependencies:
   ```bash
   pip install cryptography
   ```

3. Run the app:
   ```bash
   python app.py
   ```

---

## Usage

1. Click **Browse File** to select any file
2. Enter a strong password and confirm it
3. Click **Encrypt File** — a `.enc` file will be created in the same folder
4. To decrypt, select the `.enc` file, enter the same password, and click **Decrypt File**

---

## ⚠️ Important Notes

- There is **no password recovery** — if you forget your password, the file cannot be decrypted
- The original file is **not deleted** after encryption — you can delete it manually once confirmed
- Do not modify `.enc` files — tampering will cause decryption to fail

---

## Project Structure

```
file-encryptor/
├── app.py            # Main application
├── test_crypto.py    # AES encryption test script
└── README.md
```

---

## License

This project is open source and available under the [MIT License](LICENSE).
