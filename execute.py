import subprocess
import os
import hashlib
import json
import random
import socket
import serial
import threading
import time
import base64
from ecies import encrypt

# ===== CONFIG =====
FREQS = [93.3, 96.5, 107.5, 100.7, 87.0]  # FM frequencies in MHz
DURATION = 5                               # Seconds to record
OUTDIR = "./fm_recordings"
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 115200
KMS_PUBLIC_KEY_PATH = os.path.expanduser("/home/russo/lora-communication/key-server.hex")
# ==================

os.makedirs(OUTDIR, exist_ok=True)

# Get a unique source ID (hostname + simulated MAC)
hostname = socket.gethostname()
mac = ":".join(["{:02x}".format((hash(hostname) >> ele) & 0xff) 
                for ele in range(0, 8*6, 8)])  # Simulated MAC
SOURCE_ID = f"{hostname}-{mac}"

# Track received messages
received_hashes = set()

# Open serial port
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)

# Load KMS public key for ECC encryption
with open(KMS_PUBLIC_KEY_PATH, "r") as f:
    kms_pubkey_pem = f.read().strip()
    # ECIES library expects hex string
    kms_pubkey_hex = kms_pubkey_pem.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "")

# ---------------- FUNCTIONS ----------------

def generate_hash_file(filepath):
    """Generate SHA256 hash for a file"""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

def random_lat_lon():
    """Generate random latitude and longitude near Poland–Ukraine border"""
    # Rough bounding box along PL–UA border
    lat = round(random.uniform(49.0, 52.0), 6)   # 49°N to 52°N
    lon = round(random.uniform(22.0, 25.0), 6)   # 22°E to 25°E
    return lat, lon

def send_lora_message(message, location, file_hash):
    """Encrypt message with KMS ECC public key and send over LoRa"""
    payload_obj = {
        "source": SOURCE_ID,
        "location": location,
        "message": message,
        "hash": file_hash
    }
    payload_json = json.dumps(payload_obj).encode()

    # Encrypt with ECC public key
    ciphertext = encrypt(kms_pubkey_hex, payload_json)
    ciphertext_b64 = base64.b64encode(ciphertext).decode()

    # Wrap in JSON to send
    wrapper = {"payload": ciphertext_b64}
    msg_json = json.dumps(wrapper)
    ser.write((msg_json + "\n").encode())
    print(f"Sent ECC-encrypted message (len {len(msg_json)} chars)")

def capture_fm(freq):
    """Capture FM station for DURATION seconds and return filepath"""
    timestamp = time.strftime("%H%M%S")
    filename = f"{OUTDIR}/fm{str(freq).replace('.', '')}_{timestamp}.wav"
    print(f"Recording FM {freq} MHz -> {filename}")
    
    cmd = f"rtl_fm -f {freq}M -M wbfm -s 200k -r 48k -E deemp - | sox -t raw -r 48k -e signed -b 16 -c 1 -V1 - {filename} trim 0 {DURATION}"
    subprocess.run(cmd, shell=True, check=True)
    
    return filename

# ---------------- MAIN LOOP ----------------

def main_loop():
    while True:  # infinite loop over all frequencies
        for freq in FREQS:
            try:
                wav_file = capture_fm(freq)
                file_hash = generate_hash_file(wav_file)
                lat, lon = random_lat_lon()
                location_str = f"{lat},{lon}"
                msg_text = f"Frequency {freq} MHz captured"
                send_lora_message(msg_text, location_str, file_hash)
                time.sleep(3)  # small delay between frequencies
            except Exception as e:
                print(f"Error capturing or sending frequency {freq}: {e}")
        print("Cycle complete, sleeping 10s before next round...")
        time.sleep(10)  # wait before repeating all frequencies

# ---------------- RECEIVE & FORWARD ----------------

def read_lora():
    """Relay encrypted messages; cannot decrypt, just forward"""
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
                    ser.write((line + "\n").encode())
                    print(f"Forwarded ECC-encrypted message (len {len(wrapper['payload'])} chars)")
                except json.JSONDecodeError:
                    continue

# ---------------- START THREADS ----------------

threading.Thread(target=read_lora, daemon=True).start()
main_loop()
