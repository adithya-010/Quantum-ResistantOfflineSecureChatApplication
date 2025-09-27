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

import os
import sys
import threading
import time
import json

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.network.lan_chat import LANChat
    from src.utils.logger import setup_logger

    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n💡 Troubleshooting:")
    print("1. Make sure src/network/lan_chat.py exists")
    print("2. Make sure src/utils/logger.py exists")
    print("3. Run: python test_basic.py to check project structure")
    sys.exit(1)


class QuantumSecureChat:
    def __init__(self):
        self.logger = setup_logger("QuantumSecureChat")
        self.lan_chat = LANChat()
        self.is_running = False

    def display_banner(self):
        """Display application banner"""
        print("\n" + "=" * 60)
        print("           🔒 QUANTUM-SECURE OFFLINE CHAT APPLICATION")
        print("=" * 60)
        print("📡 Phase 1: LAN Communication Module")
        print("🔐 Phase 2: Quantum Cryptography (Coming Soon)")
        print("📱 Phase 3: QR Pairing & Steganography (Coming Soon)")
        print("=" * 60)

    def display_help(self):
        """Display help commands"""
        print("\n💡 AVAILABLE COMMANDS:")
        print("  connect <IP> <port>    - Connect to a peer (e.g., connect 192.168.1.100 12345)")
        print("  send <message>         - Send message to all connected peers")
        print("  list                   - Show connected peers")
        print("  status                 - Show application status")
        print("  help                   - Show this help message")
        print("  quit                   - Exit application")
        print("\n💡 EXAMPLE USAGE:")
        print("  > connect 192.168.1.100 12345")
        print("  > send Hello Quantum World!")
        print("  > status")

    def get_network_info(self):
        """Get local network information"""
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return hostname, local_ip
        except:
            return "Unknown", "127.0.0.1"

    def show_status(self):
        """Display current application status"""
        hostname, local_ip = self.get_network_info()

        print("\n📊 APPLICATION STATUS:")
        print(f"  Hostname: {hostname}")
        print(f"  Local IP: {local_ip}")
        print(f"  Server Port: {self.lan_chat.port}")
        print(f"  Connected Peers: {len(self.lan_chat.connections)}")
        print(f"  Server Running: {'✅' if self.is_running else '❌'}")

    def start(self):
        """Start the chat application"""
        self.display_banner()

        try:
            # Start the LAN chat server
            server_thread = threading.Thread(target=self.lan_chat.start_server)
            server_thread.daemon = True
            server_thread.start()
            self.is_running = True

            # Give server time to start
            time.sleep(1)

            hostname, local_ip = self.get_network_info()
            print(f"📍 Your connection info: {local_ip}:{self.lan_chat.port}")
            print("💡 Others can connect to you using this address")

            self.display_help()

            # Main command loop
            self.command_loop()

        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            self.shutdown()

    def command_loop(self):
        """Main command processing loop"""
        while True:
            try:
                user_input = input("\n🔹 quantum-chat> ").strip()

                if not user_input:
                    continue

                parts = user_input.split()
                command = parts[0].lower()

                if command == "connect" and len(parts) == 3:
                    self.connect_to_peer(parts[1], parts[2])

                elif command == "send" and len(parts) > 1:
                    message = " ".join(parts[1:])
                    self.send_message(message)

                elif command == "list":
                    self.list_connections()

                elif command == "status":
                    self.show_status()

                elif command == "help":
                    self.display_help()

                elif command == "quit":
                    break

                else:
                    print("❌ Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested...")
                break
            except Exception as e:
                print(f"❌ Error processing command: {e}")

        self.shutdown()

    def connect_to_peer(self, ip, port_str):
        """Connect to another chat instance"""
        try:
            port = int(port_str)
            self.lan_chat.connect_to_peer(ip, port)
            print(f"✅ Connecting to {ip}:{port}...")
        except ValueError:
            print("❌ Invalid port number. Use: connect <IP> <port>")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")

    def send_message(self, message):
        """Send a message to all connected peers"""
        if not self.lan_chat.connections:
            print("⚠️  No connected peers. Use 'connect <IP> <port>' first.")
            return

        try:
            self.lan_chat.send_message(message)
            print(f"📤 Message sent: {message}")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")

    def list_connections(self):
        """List all active connections"""
        if not self.lan_chat.connections:
            print("📭 No active connections")
            return

        print(f"🔗 Active connections: {len(self.lan_chat.connections)}")
        # Note: In a real implementation, we'd track connection info better

    def shutdown(self):
        """Clean shutdown of the application"""
        print("\n🛑 Shutting down Quantum-Secure Chat...")
        self.is_running = False
        self.lan_chat.stop()
        print("👋 Application closed successfully!")
        print("💡 Thank you for using Quantum-Secure Chat!")


def main():
    """Main entry point"""
    try:
        app = QuantumSecureChat()
        app.start()
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("💡 Try running: python test_basic.py to diagnose issues")


if __name__ == "__main__":
    main()