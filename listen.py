import serial
import json

# ===== CONFIG =====
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 115200
# ==================

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.1)
print("Observer listening on LoRa... (cannot decrypt messages)")

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
                if "payload" in wrapper:
                    payload_preview = wrapper["payload"][:60]  # print first 60 chars
                    print(f"[ENCRYPTED] payload preview: {payload_preview}...")
                else:
                    print("[ENCRYPTED] no payload field")
            except json.JSONDecodeError:
                print("[ENCRYPTED] malformed JSON")
