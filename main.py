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
# main.py
import sys
from src.utils.logger import get_logger
from src.network.lan_chat import LanChat

def main():
    logger = get_logger("QuantumSecureChat")
    logger.info("Starting Quantum Secure Chat Application (Phase 2 - Quantum Crypto)")

    # Ask user for name
    username = input("Enter your name: ").strip()
    if not username:
        username = "User"

    # Initialize LAN chat (Phase 2 ready)
    chat = LanChat(username, logger)
    logger.info(f"Chat initialized for user: {username}")

    print("Type 'help' for list of commands.\n")

    while True:
        try:
            cmd = input(f"{username}> ").strip()
            if not cmd:
                continue

            parts = cmd.split(" ", 2)
            command = parts[0].lower()

            if command == "connect" and len(parts) >= 3:
                ip = parts[1]
                port = int(parts[2])
                chat.connect(ip, port)

            elif command == "send" and len(parts) >= 2:
                message = parts[1]
                # Phase 2: send encrypted message
                chat.send_message(message)

            elif command == "status":
                chat.show_status()

            elif command == "list":
                chat.list_peers()

            elif command == "help":
                print("""
Available commands:
connect <IP> <port>  - Connect to another peer
send <message>       - Send encrypted message to all peers
status               - Show connection status
list                 - List connected devices
help                 - Show this help
quit                 - Exit application
""")

            elif command == "quit":
                print("Exiting chat...")
                chat.shutdown()
                break

            else:
                print("Unknown command. Type 'help' for commands.")

        except KeyboardInterrupt:
            print("\nExiting chat...")
            chat.shutdown()
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
