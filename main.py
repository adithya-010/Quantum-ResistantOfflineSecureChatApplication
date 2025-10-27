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

# !/usr/bin/env python3
"""
Quantum-Secure Offline Chat Application
Main entry point with all features integrated
"""

import os
import sys
import threading
import time
import json
import argparse

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.network.lan_chat import LANChat
    from src.crypto.pqc import QuantumCrypto
    from src.steganography.stego import Steganography
    from src.pairing.qr_pairing import QRPairing
    from src.utils.logger import setup_logger

    print("✅ All modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Run: python project_status_checker.py to diagnose issues")
    sys.exit(1)


class QuantumSecureChat:
    def __init__(self, port=23456, enable_crypto=True):
        self.logger = setup_logger("QuantumSecureChat")
        self.lan_chat = LANChat(port=port)
        self.quantum_crypto = QuantumCrypto() if enable_crypto else None
        self.steganography = Steganography()
        self.qr_pairing = QRPairing()
        self.is_running = False
        self.encryption_enabled = enable_crypto

    def display_banner(self):
        """Display application banner"""
        print("\n" + "=" * 60)
        print("           🔒 QUANTUM-SECURE OFFLINE CHAT")
        print("=" * 60)
        print("📡 LAN Communication | 🔐 Quantum Crypto | 📱 QR Pairing")
        print("=" * 60)
        if self.encryption_enabled:
            print("🔒 ENCRYPTION: ENABLED")
        else:
            print("⚠️  ENCRYPTION: DISABLED (Testing Mode)")
        print("=" * 60)

    def display_help(self):
        """Display help commands"""
        print("\n💡 AVAILABLE COMMANDS:")
        print("  connect <IP> <port>    - Connect to a peer")
        print("  send <message>         - Send message to all peers")
        print("  hide <image> <msg>     - Hide message in image")
        print("  reveal <image>         - Reveal message from image")
        print("  qr_gen <data>          - Generate QR code")
        print("  qr_scan                - Scan QR code from camera")
        print("  status                 - Show application status")
        print("  crypto_status          - Show crypto capabilities")
        print("  help                   - Show this help message")
        print("  quit                   - Exit application")

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
        print(f"  Connected Peers: {self.lan_chat.get_connection_count()}")
        print(f"  Encryption: {'✅ ENABLED' if self.encryption_enabled else '❌ DISABLED'}")
        print(f"  Server Running: {'✅' if self.is_running else '❌'}")

    def show_crypto_status(self):
            """Display quantum cryptography status using oqs library"""
            print("\n🔐 QUANTUM CRYPTOGRAPHY STATUS:")

            if not self.quantum_crypto:
                print("❌ Quantum cryptography is disabled")
                return

            try:
                import oqs
                print("✅ OQS library: LOADED")

                # Fetch supported algorithms
                kems = oqs.get_enabled_kem_mechanisms()
                sigs = oqs.get_enabled_sig_mechanisms()

                if not kems or not sigs:
                    print("⚠️  No KEM or signature mechanisms found. Check your liboqs installation.")
                    return

                print(f"\n🧩 Supported KEMs ({len(kems)}):")
                for kem in kems[:10]:
                    print(f"   - {kem}")
                if len(kems) > 10:
                    print(f"   ... and {len(kems) - 10} more")

                print(f"\n🧩 Supported Signature Schemes ({len(sigs)}):")
                for sig in sigs[:10]:
                    print(f"   - {sig}")
                if len(sigs) > 10:
                    print(f"   ... and {len(sigs) - 10} more")

                # Quick KEM test
                print("\n⚙️  Performing KEM handshake test (Kyber512)...")
                kem = oqs.KeyEncapsulation("Kyber512")
                public_key = kem.generate_keypair()
                ciphertext, shared_secret_sender = kem.encap_secret(public_key)
                shared_secret_receiver = kem.decap_secret(ciphertext)

                if shared_secret_sender == shared_secret_receiver:
                    print("✅ Handshake successful — shared secrets match")
                else:
                    print("❌ Handshake failed — shared secrets mismatch")

            except ImportError:
                print("❌ OQS library: NOT FOUND. Please ensure liboqs and pybind11-oqs are installed.")
            except AttributeError as e:
                print(f"❌ Attribute error: {e}")
            except Exception as e:
                print(f"❌ Error processing command: {e}")

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

                elif command == "hide" and len(parts) > 2:
                    image_path = parts[1]
                    message = " ".join(parts[2:])
                    self.hide_message(image_path, message)

                elif command == "reveal" and len(parts) == 2:
                    image_path = parts[1]
                    self.reveal_message(image_path)

                elif command == "qr_gen" and len(parts) > 1:
                    data = " ".join(parts[1:])
                    self.generate_qr_code(data)

                elif command == "qr_scan":
                    self.scan_qr_code()

                elif command == "status":
                    self.show_status()

                elif command == "crypto_status":
                    self.show_crypto_status()

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
            result = self.lan_chat.connect_to_peer(ip, port)
            if result:
                print(f"✅ Connecting to {ip}:{port}...")
            else:
                print(f"❌ Failed to connect to {ip}:{port}")
        except ValueError:
            print("❌ Invalid port number. Use: connect <IP> <port>")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")

    def send_message(self, message):
        """Send a plaintext message"""
        if not self.lan_chat.connections:
            print("⚠️  No connected peers. Use 'connect <IP> <port>' first.")
            return

        try:
            success = self.lan_chat.send_message(message)
            if success:
                print(f"📤 Message sent: {message}")
            else:
                print("❌ Failed to send message")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")

    def hide_message(self, image_path, message):
        """Hide a message in an image"""
        try:
            result = self.steganography.hide_message(image_path, message)
            if result:
                print(f"✅ Message hidden in: {result}")
            else:
                print("❌ Failed to hide message")
        except Exception as e:
            print(f"❌ Error hiding message: {e}")

    def reveal_message(self, image_path):
        """Reveal a message from an image"""
        try:
            message = self.steganography.reveal_message(image_path)
            if message:
                print(f"🔍 Revealed message: {message}")
            else:
                print("❌ No message found or failed to reveal")
        except Exception as e:
            print(f"❌ Error revealing message: {e}")

    def generate_qr_code(self, data):
        """Generate a QR code"""
        try:
            result = self.qr_pairing.generate_qr_code(data, "generated_qr.png")
            if result:
                print(f"✅ QR code generated: {result}")
            else:
                print("❌ Failed to generate QR code")
        except Exception as e:
            print(f"❌ Error generating QR code: {e}")

    def scan_qr_code(self):
        """Scan QR code from camera"""
        print("📷 Starting camera for QR scanning...")
        result = self.qr_pairing.scan_qr_code(timeout=30)
        if result:
            print(f"✅ QR code scanned: {result}")
        else:
            print("❌ No QR code scanned or scan cancelled")

    def shutdown(self):
        """Clean shutdown of the application"""
        print("\n🛑 Shutting down Quantum-Secure Chat...")
        self.is_running = False
        self.lan_chat.stop()
        print("👋 Application closed successfully!")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Quantum-Secure Chat Application')
    parser.add_argument('--port', type=int, default=23456, help='Port to use (default: 23456)')
    parser.add_argument('--no-crypto', action='store_true', help='Disable quantum cryptography')
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()

    try:
        app = QuantumSecureChat(port=args.port, enable_crypto=not args.no_crypto)
        app.start()
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("💡 Try running: python project_status_checker.py")


if __name__ == "__main__":
    main()
