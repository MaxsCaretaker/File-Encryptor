import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# ── Theme ───────────────────────────────────────────
BG = "#1e1e2e"
CARD = "#2a2a3e"
ACCENT = "#9d4edd"
TEXT = "#ffffff"
SUBTEXT = "#aaaacc"
GREEN = "#4caf50"
RED = "#ef5350"
YELLOW = "#ffd166"

# ── Crypto ───────────────────────────────────────────
def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(password.encode())

def encrypt_file(filepath: str, password: str) -> str:
    with open(filepath, "rb") as f:
        data = f.read()

    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, data, None)

    out_path = filepath + ".enc"
    with open(out_path, "wb") as f:
        f.write(salt + nonce + encrypted)

    return out_path

def decrypt_file(filepath: str, password: str) -> str:
    with open(filepath, "rb") as f:
        data = f.read()

    salt = data[:16]
    nonce = data[16:28]
    encrypted = data[28:]
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    decrypted = aesgcm.decrypt(nonce, encrypted, None)

    out_path = filepath.replace(".enc", ".decrypted")
    if not out_path.endswith(".decrypted"):
        out_path += ".decrypted"

    with open(out_path, "wb") as f:
        f.write(decrypted)

    return out_path

# ── Root ─────────────────────────────────────────────
root = tk.Tk()
root.title("🔐 File Encryptor")
root.geometry("620x580")
root.configure(bg=BG)
root.resizable(False, False)

# ── State ────────────────────────────────────────────
selected_file = tk.StringVar(value="")

# ── Helpers ──────────────────────────────────────────
def browse_file():
    path = filedialog.askopenfilename()
    if path:
        selected_file.set(path)
        filename = os.path.basename(path)
        size = os.path.getsize(path)
        size_str = f"{size:,} bytes" if size < 1024 else \
                   f"{size/1024:.1f} KB" if size < 1024**2 else \
                   f"{size/1024**2:.1f} MB"
        file_label.config(text=f"📄 {filename}  ({size_str})", fg=TEXT)
        status_var.set("")

def set_status(msg, color=SUBTEXT):
    status_var.set(msg)
    status_label.config(fg=color)
    root.update()

def run_encrypt():
    filepath = selected_file.get()
    password = password_var.get()
    confirm = confirm_var.get()

    if not filepath:
        messagebox.showwarning("No File", "Please select a file first.")
        return
    if not password:
        messagebox.showwarning("No Password", "Please enter a password.")
        return
    if password != confirm:
        messagebox.showerror("Mismatch", "Passwords do not match.")
        return
    if filepath.endswith(".enc"):
        messagebox.showwarning("Already Encrypted", "This file appears to already be encrypted.")
        return

    encrypt_btn.config(state="disabled")
    decrypt_btn.config(state="disabled")
    set_status("Encrypting...", YELLOW)

    def task():
        try:
            out_path = encrypt_file(filepath, password)
            filename = os.path.basename(out_path)
            root.after(0, lambda: set_status(f"✅ Encrypted → {filename}", GREEN))
            root.after(0, lambda: add_to_log("ENCRYPTED", os.path.basename(filepath), GREEN))
        except Exception as e:
            root.after(0, lambda: set_status(f"❌ Encryption failed: {e}", RED))
        finally:
            root.after(0, lambda: encrypt_btn.config(state="normal"))
            root.after(0, lambda: decrypt_btn.config(state="normal"))

    threading.Thread(target=task, daemon=True).start()

def run_decrypt():
    filepath = selected_file.get()
    password = password_var.get()

    if not filepath:
        messagebox.showwarning("No File", "Please select a file first.")
        return
    if not password:
        messagebox.showwarning("No Password", "Please enter a password.")
        return
    if not filepath.endswith(".enc"):
        if not messagebox.askyesno("Warning", "This file doesn't have a .enc extension. Try to decrypt anyway?"):
            return

    encrypt_btn.config(state="disabled")
    decrypt_btn.config(state="disabled")
    set_status("Decrypting...", YELLOW)

    def task():
        try:
            out_path = decrypt_file(filepath, password)
            filename = os.path.basename(out_path)
            root.after(0, lambda: set_status(f"✅ Decrypted → {filename}", GREEN))
            root.after(0, lambda: add_to_log("DECRYPTED", os.path.basename(filepath), ACCENT))
        except Exception:
            root.after(0, lambda: set_status("❌ Decryption failed — wrong password or corrupted file.", RED))
        finally:
            root.after(0, lambda: encrypt_btn.config(state="normal"))
            root.after(0, lambda: decrypt_btn.config(state="normal"))

    threading.Thread(target=task, daemon=True).start()

def add_to_log(action, filename, color):
    log_frame_inner.config(bg=BG)
    row = tk.Frame(log_frame_inner, bg=CARD, pady=4, padx=10)
    row.pack(fill="x", pady=2)
    tk.Label(row, text=action, font=("Segoe UI", 9, "bold"),
             bg=CARD, fg=color, width=10, anchor="w").pack(side="left")
    tk.Label(row, text=filename, font=("Segoe UI", 9),
             bg=CARD, fg=TEXT, anchor="w").pack(side="left")

def toggle_password():
    if password_entry.cget("show") == "*":
        password_entry.config(show="")
        confirm_entry.config(show="")
        show_btn.config(text="🙈 Hide")
    else:
        password_entry.config(show="*")
        confirm_entry.config(show="*")
        show_btn.config(text="👁 Show")

# ── Header ───────────────────────────────────────────
header = tk.Frame(root, bg=ACCENT, pady=15)
header.pack(fill="x")
tk.Label(header, text="🔐  File Encryptor",
         font=("Segoe UI", 22, "bold"), bg=ACCENT, fg=TEXT).pack()
tk.Label(header, text="AES-256 encryption for your files",
         font=("Segoe UI", 10), bg=ACCENT, fg="#ddd").pack()

# ── File Selection ───────────────────────────────────
file_card = tk.Frame(root, bg=CARD, padx=20, pady=15)
file_card.pack(fill="x", padx=20, pady=15)

tk.Label(file_card, text="Select File", font=("Segoe UI", 12, "bold"),
         bg=CARD, fg=ACCENT).pack(anchor="w", pady=(0, 8))

file_label = tk.Label(file_card, text="No file selected",
    font=("Segoe UI", 10), bg=CARD, fg=SUBTEXT, anchor="w")
file_label.pack(fill="x", pady=(0, 8))

tk.Button(file_card, text="📂  Browse File", command=browse_file,
    bg="#3a3a55", fg=TEXT, font=("Segoe UI", 10),
    relief="flat", padx=12, pady=6, cursor="hand2").pack(anchor="w")

# ── Password ─────────────────────────────────────────
pass_card = tk.Frame(root, bg=CARD, padx=20, pady=15)
pass_card.pack(fill="x", padx=20)

tk.Label(pass_card, text="Password", font=("Segoe UI", 12, "bold"),
         bg=CARD, fg=ACCENT).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

tk.Label(pass_card, text="Enter Password", bg=CARD, fg=SUBTEXT,
         font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", padx=(0, 20))
tk.Label(pass_card, text="Confirm Password", bg=CARD, fg=SUBTEXT,
         font=("Segoe UI", 9)).grid(row=1, column=1, sticky="w")

password_var = tk.StringVar()
confirm_var = tk.StringVar()

password_entry = tk.Entry(pass_card, textvariable=password_var, show="*", width=25,
    bg="#3a3a55", fg=TEXT, insertbackground=TEXT, relief="flat",
    font=("Segoe UI", 11))
password_entry.grid(row=2, column=0, ipady=6, padx=(0, 20))

confirm_entry = tk.Entry(pass_card, textvariable=confirm_var, show="*", width=25,
    bg="#3a3a55", fg=TEXT, insertbackground=TEXT, relief="flat",
    font=("Segoe UI", 11))
confirm_entry.grid(row=2, column=1, ipady=6)

show_btn = tk.Button(pass_card, text="👁 Show", command=toggle_password,
    bg=BG, fg=SUBTEXT, font=("Segoe UI", 9), relief="flat", cursor="hand2")
show_btn.grid(row=3, column=0, sticky="w", pady=(5, 0))

# ── Action Buttons ───────────────────────────────────
btn_frame = tk.Frame(root, bg=BG)
btn_frame.pack(pady=15)

encrypt_btn = tk.Button(btn_frame, text="🔒  Encrypt File", command=run_encrypt,
    bg=GREEN, fg=TEXT, font=("Segoe UI", 11, "bold"),
    relief="flat", padx=20, pady=8, cursor="hand2")
encrypt_btn.pack(side="left", padx=10)

decrypt_btn = tk.Button(btn_frame, text="🔓  Decrypt File", command=run_decrypt,
    bg=ACCENT, fg=TEXT, font=("Segoe UI", 11, "bold"),
    relief="flat", padx=20, pady=8, cursor="hand2")
decrypt_btn.pack(side="left", padx=10)

# ── Status ───────────────────────────────────────────
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var,
    font=("Segoe UI", 10), bg=BG, fg=SUBTEXT)
status_label.pack()

# ── Activity Log ─────────────────────────────────────
tk.Label(root, text="Activity Log", font=("Segoe UI", 11, "bold"),
         bg=BG, fg=ACCENT).pack(anchor="w", padx=20, pady=(10, 3))

log_frame_inner = tk.Frame(root, bg=BG)
log_frame_inner.pack(fill="x", padx=20)

root.mainloop()