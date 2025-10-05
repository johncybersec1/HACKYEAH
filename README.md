# Reconet-HACKYEAH
# 📡 Portable Signal Recorder

> A compact device concept that quietly monitors radio/frequency activity, creates tamper-evident records, and shares lightweight proofs over a resilient mesh network for later verification.

---

## 🧠 Overview
Imagine a tiny box that fits in your backpack. Its job: to quietly watch the radio environment and keep a trustworthy record of anything unusual — like jamming, strange transmissions, or unidentified signals.  
All data stays securely locked inside, while a small cryptographic “fingerprint” (hash) is shared across a low-power mesh network so the record can later be verified but never falsified.

---

## ⚙️ How It Works
1. **Listen:** The device monitors the surrounding frequencies and detects anomalies or any signal activity.  
2. **Fingerprint:** For each event, it generates a secure digital hash to ensure tamper-proof integrity.  
3. **Secure Storage:** Full recordings remain encrypted inside the device; only authorized users with the correct key/token can retrieve them.  
4. **Broadcast Proof:** Metadata (hash + timestamp) is sent over a LoRa-style mesh network, extending communication even when Wi-Fi or cellular fails.  
5. **Retrieve & Verify:** Authorized parties can later unlock the data and verify it against the published fingerprint for forensic integrity.

---

## 🛰️ Use Cases
- **Area Security:** Monitor a defined area to confirm no unauthorized signals or drones are active.  
- **Forensics:** Preserve tamper-evident evidence of radio events for later investigation.  
- **Resilience:** Maintain trusted signal records even in jammed or offline network environments.  
- **Mobility:** Deploy on drones, vehicles, or mobile gateways to expand range and coverage.

---

## 🔐 Why It’s Useful
- Functions when conventional networks are down or disrupted.  
- Provides **tamper-evident**, cryptographically verifiable data.  
- Portable, efficient, and adaptable to various mission profiles.  
- Mesh-based communication improves reliability and persistence.

---

## 🛡️ Security & Privacy Model
- **Tamper Evidence:** Public hashes prove data integrity and timestamp.  
- **Encryption:** Raw signal data is stored securely and privately.  
- **Separation of Proof & Data:** Hashes reveal nothing about actual contents.  
- **Access Control:** Retrieval requires valid cryptographic credentials.

---

## ⚖️ Ethics & Legal Notice
This concept involves signal monitoring and recording.  
Before designing or deploying such a system:
- ✅ Follow **all applicable laws and regulations** in your jurisdiction.  
- ✅ **Respect privacy and human rights**; never use for unauthorized surveillance.  
- ✅ Conduct **ethical and legal review** for deployments in sensitive or conflict areas.  

> This project is **a conceptual design**, not a ready-to-use surveillance or interception tool.

---

## 🧩 Roadmap (Conceptual)
- [ ] Hardware prototyping (low-power RF capture + storage)  
- [ ] Cryptographic hashing module  
- [ ] Secure local data vault  
- [ ] LoRa/mesh proof broadcasting  
- [ ] Forensic data retrieval + verification tool  

---

## Where the files run and how
# Listener 1 (Raspberry Pi):
Execute.py listens to the Radio FM frequencies and broadcasts encrypted message to the Central Server.

# Listener 2 (Raspberry Pi):
Execute.py listens to the Radio FM frequencies and broadcasts encrypted message to the Central Server.

# Central Server (Raspberry Pi):
Listen.py listens to the messages from the receivers, decrypts it and pushes it to the database.

# app.py:
Creates the Flask application and waits for http connections and web socket connections. Web sockets are used for real-time updates.

# index.html:
This is the layout of our Dashboard interface.
## 🧾 License
Open for research, education, and ethical experimentation only.  
All use must comply with relevant **radio laws, privacy frameworks, and ethical standards**.

---

**Author:** *Rodrigo Russo*  
**Repository Type:** Concept / Research Prototype  
**Version:** 0.1 – Draft  
