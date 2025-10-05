import serial
import json
import base64
import sqlite3
from ecies import decrypt
import time
import os

# ===== CONFIG =====
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 115200
KMS_PRIVATE_KEY_PATH = "/home/russo/ecc-256/ecc_private.hex"
DB_PATH = "./data.db"
# ==================

# Load private key
with open(KMS_PRIVATE_KEY_PATH, "r") as f:
    kms_priv_hex = f.read().strip()

# Serial port
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)

# DB setup
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT UNIQUE,
        first_seen TEXT,
        last_seen TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source TEXT,
        location TEXT,
        message TEXT,
        filehash TEXT
    )""")
    conn.commit()
    conn.close()

def upsert_device(source, ts):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id FROM devices WHERE source=?", (source,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE devices SET last_seen=? WHERE source=?", (ts, source))
    else:
        cur.execute("INSERT INTO devices (source, first_seen, last_seen) VALUES (?, ?, ?)", (source, ts, ts))
    conn.commit()
    conn.close()

def insert_message(ts, src, location, message, filehash):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (timestamp, source, location, message, filehash) VALUES (?, ?, ?, ?, ?)",
                (ts, src, location, message, filehash))
    conn.commit()
    conn.close()

init_db()
print("KMS listening for ECC-encrypted messages...")

buffer = ""
while True:
    if ser.in_waiting:
        chunk = ser.read(ser.in_waiting).decode(errors='ignore')
        buffer += chunk
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                wrapper = json.loads(line)
                if "payload" not in wrapper:
                    continue
                try:
                    ciphertext = base64.b64decode(wrapper["payload"])
                except Exception as e:
                    print("Base64 decode failed:", e)
                    continue
                try:
                    plaintext_bytes = decrypt(kms_priv_hex, ciphertext)
                    msg_obj = json.loads(plaintext_bytes.decode())
                    ts = time.strftime("%Y-%m-%d %H:%M:%S")
                    src = msg_obj.get("source")
                    loc = msg_obj.get("location")
                    msg = msg_obj.get("message")
                    filehash = msg_obj.get("hash")

                    print(f"[DECRYPTED] From {src} at {loc}: {msg}")

                    # Store
                    upsert_device(src, ts)
                    insert_message(ts, src, loc, msg, filehash)

                except Exception as e:
                    print("Decryption failed:", e)

            except json.JSONDecodeError:
                continue


