#!/usr/bin/env python3
"""
Quantum-Secure Offline Chat Application
Phase 1: LAN Communication Module

Team:
- ADITHYA. M (RA2211004010164)
- AYUSH PRATAP (RA2211004010169)
- PUVIYARASSHAN.B.A (RA2211004010201)

Features:
- Offline LAN Communication
- Post-Quantum Cryptography (Coming in Phase 2)
- QR Code Pairing (Coming in Phase 3)
- Steganography Messaging (Coming in Phase 3)
"""
import threading
from utils.logger import get_logger
from network.lan_chat import LANChat

logger = get_logger("MAIN")

def main():
    logger.info("🚀 Quantum-Secure Chat (Phase 1 – LAN Module)")
    username = input("Enter your display name: ").strip() or "Anonymous"

    # Start LAN chat engine
    chat = LANChat(username=username)
    threading.Thread(target=chat.start_server, daemon=True).start()

    logger.info("Type 'help' for available commands.")
    while True:
        try:
            cmd = input("> ").strip()
            if not cmd:
                continue

            if cmd.startswith("connect"):
                _, ip, port = cmd.split()
                chat.connect_to_peer(ip, int(port))

            elif cmd.startswith("send"):
                msg = cmd.partition(" ")[2]
                chat.broadcast_message(msg)

            elif cmd == "list":
                chat.list_peers()

            elif cmd == "status":
                chat.show_status()

            elif cmd == "help":
                print("""
Commands:
 connect <IP> <PORT>  → connect to peer
 send <message>       → send a chat message
 list                 → list connected peers
 status               → connection status
 quit                 → exit
                """)

            elif cmd == "quit":
                logger.info("Shutting down...")
                chat.close_all()
                break

            else:
                logger.warning("Unknown command. Type 'help' for options.")

        except Exception as e:
            logger.error(f"Command error: {e}")

if __name__ == "__main__":
    main()
