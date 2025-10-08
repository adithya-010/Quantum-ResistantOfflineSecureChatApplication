# Quantum-Resistant Offline Secure Chat Application

## Project Overview
**Title:** Quantum-Resistant Offline Secure Chat Application with QR-Based Pairing and Steganographic Messaging  
**Team Members:**  
- ADITHYA M  
- AYUSH PRATAP  
- PUVIYARASSHAN B A  

**Course:** 21ECC402P - Computer Communication and Network Security  

---

## Project Vision & Innovation
**Problem:** Traditional encryption (RSA, ECC) will be broken by quantum computers.  
**Solution:** Provide quantum-resistant, offline chat with:  
- Post-Quantum Cryptography (Kyber & Dilithium)  
- Offline LAN communication  
- QR Code pairing to prevent MITM attacks  
- Steganography for hiding messages  
- Group chat with rotating session keys  

---

## Phase 1: LAN Communication Module
- Language: Python 3.10  
- Networking: Raw sockets with threading (peer-to-peer)  
- Features:
  - Multi-client support  
  - Real-time bidirectional messaging  
  - Connection management  
  - Command interface

**Commands:**
```
connect <IP> <port>
send <message>
status
list
help
quit
```

---

## Phase 2: Quantum Cryptography Integration
- Kyber for key exchange (quantum-safe)  
- Dilithium for digital signatures  
- AES encryption for messages  
- LAN chat commands remain the same  

---

## Technical Stack
- Python 3.10  
- Libraries: colorlog, numpy, opencv-python, Pillow, qrcode[pil], stegano, cryptography, psutil, liboqs-python  

---

## How to Run
1. Install dependencies:  
```bash
python install_dependencies.py
```
2. Run main application:  
```bash
python main.py
```
3. Use commands:  
```
connect <IP> <port>
send <message>
status
list
help
quit
```

---

## Project Status
- Phase 1: ✅ Complete and tested  
- Phase 2: 🚀 Quantum-safe messaging ready for testing  

---

## Future Roadmap
- QR code secure pairing  
- Steganographic message hiding  
- GUI interface (PyQt5)  
- Advanced intrusion detection  
- Mobile and enterprise versions
