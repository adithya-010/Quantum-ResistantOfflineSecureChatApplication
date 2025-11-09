#!/usr/bin/env python3
"""
Quantum-Secure Offline Chat Application
Main entry point with all features integrated
"""

import os
import sys
import threading
import time
import argparse
import socket
import traceback

# Make local src importable whether run as script or module
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from src.network.lan_chat import LANChat
from src.crypto.pqc import QuantumCrypto
from src.steganography.stego import Steganography  # keep your existing file
from src.pairing.qr_pairing import QRPairing
from src.utils.logger import setup_logger  # keep your existing file


class QuantumSecureChat:
    def __init__(self, port: int = 23456, enable_crypto: bool = True):
        self.logger = setup_logger("QuantumSecureChat")
        self.port = port

        # Core modules (robust to failures)
        self.lan_chat = LANChat(port=port)
        self.quantum_crypto = QuantumCrypto() if enable_crypto else None
        self.steganography = Steganography()
        self.qr_pairing = QRPairing()

        self.is_running = False
        self.encryption_enabled = enable_crypto

    # ---------------- UI helpers ----------------
    def display_banner(self):
        print("\n" + "=" * 60)
        print("           🔒 QUANTUM-SECURE OFFLINE CHAT")
        print("=" * 60)
        print("📡 LAN Communication | 🔐 Quantum Crypto | 📱 QR Pairing")
        print("=" * 60)
        if self.encryption_enabled and self.quantum_crypto:
            print("🔒 ENCRYPTION: ENABLED")
        else:
            print("⚠️  ENCRYPTION: DISABLED (Testing Mode)")
        print("=" * 60)

    def display_help(self):
        print("\n💡 AVAILABLE COMMANDS:")
        print("  connect <IP> <port>    - Connect to a peer")
        print("  send <message>         - Send message to all peers")
        print("  send_img <path>        - Send an image file (PNG) to peers")  # ← added
        print("  hide <image> <msg>     - Hide message in image")
        print("  reveal <image>         - Reveal message from image")
        print("  qr_gen <ip> <port>     - Generate QR code (auto-connect payload)")
        print("  qr_scan                - Scan QR from camera and auto-connect")
        print("  status                 - Show application status")
        print("  crypto_status          - Show crypto capabilities")
        print("  help                   - Show this help message")
        print("  quit                   - Exit application")

    def get_network_info(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = "127.0.0.1"
        finally:
            try:
                s.close()
            except Exception:
                pass
        return socket.gethostname(), local_ip

    def show_status(self):
        hostname, local_ip = self.get_network_info()
        print("\n📊 APPLICATION STATUS:")
        print(f"  Hostname: {hostname}")
        print(f"  Local IP: {local_ip}")
        print(f"  Server Port: {self.lan_chat.port}")
        try:
            conn_count = self.lan_chat.get_connection_count()
        except Exception:
            conn_count = "unknown"
        print(f"  Connected Peers: {conn_count}")
        print(f"  Encryption: {'✅ ENABLED' if (self.encryption_enabled and self.quantum_crypto) else '❌ DISABLED'}")
        print(f"  Server Running: {'✅' if self.is_running else '❌'}")

    # ---------------- Crypto status (version-tolerant) ----------------
    def show_crypto_status(self):
        """Display quantum cryptography status using oqs library (version tolerant)."""
        print("\n🔐 QUANTUM CRYPTOGRAPHY STATUS:")

        if not self.encryption_enabled or not self.quantum_crypto:
            print("❌ Quantum cryptography is disabled or not initialized")
            return

        try:
            import oqs  # type: ignore
            print("✅ OQS library: LOADED")
            attrs = [a for a in dir(oqs) if not a.startswith("_")]
            print(f"🧠 oqs module attributes: {attrs}")

            # Try to list KEMs / SIGs, across versions
            kems = []
            sigs = []
            if hasattr(oqs, "get_enabled_kem_mechanisms"):
                try:
                    kems = oqs.get_enabled_kem_mechanisms()
                except Exception:
                    pass
            if not kems and hasattr(oqs, "get_enabled_KEM_mechanisms"):
                try:
                    kems = oqs.get_enabled_KEM_mechanisms()
                except Exception:
                    pass
            if hasattr(oqs, "get_enabled_sig_mechanisms"):
                try:
                    sigs = oqs.get_enabled_sig_mechanisms()
                except Exception:
                    pass
            if not sigs and hasattr(oqs, "get_enabled_SIG_mechanisms"):
                try:
                    sigs = oqs.get_enabled_SIG_mechanisms()
                except Exception:
                    pass

            if not kems and not sigs and hasattr(oqs, "Kem"):
                # Probe modern Kem
                try:
                    kem_inst = oqs.Kem("Kyber512")
                    name = getattr(getattr(kem_inst, "details", {}), "get", lambda *_: None)("name")
                    kems = [name or getattr(kem_inst, "name", "Kyber512")]
                except Exception:
                    pass

            if not kems and not sigs:
                print("⚠️  No KEM or signature mechanisms found. OQS bindings may not be linked to liboqs.")
            else:
                if kems:
                    print(f"\n🧩 Supported KEMs ({len(kems)}):")
                    for kem in kems[:20]:
                        print(f"   - {kem}")
                    if len(kems) > 20:
                        print(f"   ... and {len(kems) - 20} more")
                if sigs:
                    print(f"\n🧩 Supported Signature Schemes ({len(sigs)}):")
                    for sig in sigs[:20]:
                        print(f"   - {sig}")
                    if len(sigs) > 20:
                        print(f"   ... and {len(sigs) - 20} more")

            # Handshake smoke test is already exercised in runtime via LANChat handshake
            print("\nℹ️  Runtime uses Kyber512 if OQS is available; else X25519 + AES-GCM.")

        except ImportError:
            print("❌ OQS library: NOT FOUND. App will use X25519 + AES-GCM fallback.")
        except Exception:
            print("❌ Unexpected error while checking OQS:")
            traceback.print_exc()

    # ---------------- Core app lifecycle ----------------
    def start(self):
        self.display_banner()
        try:
            server_thread = threading.Thread(target=self.lan_chat.start_server, daemon=True)
            server_thread.start()
            self.is_running = True

            time.sleep(1)
            _, local_ip = self.get_network_info()
            print(f"📍 Your connection info: {local_ip}:{self.lan_chat.port}")
            print("💡 Others can connect to you using this address")
            self.display_help()
            self.command_loop()

        except KeyboardInterrupt:
            self.shutdown()
        except Exception:
            self.logger.exception("Application error occurred during start.")
            self.shutdown()

    def command_loop(self):
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

                elif command == "send_img" and len(parts) == 2:  # ← added
                    self.send_image_to_peers(parts[1])

                elif command == "hide" and len(parts) > 2:
                    image_path = parts[1]
                    message = " ".join(parts[2:])
                    self.hide_message(image_path, message)

                elif command == "reveal" and len(parts) == 2:
                    image_path = parts[1]
                    self.reveal_message(image_path)

                elif command == "qr_gen" and len(parts) == 3:
                    ip, port_s = parts[1], parts[2]
                    self.generate_qr_code(ip, port_s)

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

    # ---------------- Commands ----------------
    def connect_to_peer(self, ip, port_str):
        try:
            port = int(port_str)
            result = self.lan_chat.connect_to_peer(ip, port)
            if result:
                print(f"✅ Connected to {ip}:{port}")
            else:
                print(f"❌ Failed to connect to {ip}:{port}")
        except ValueError:
            print("❌ Invalid port number. Use: connect <IP> <port>")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")

    def send_message(self, message):
        try:
            success = self.lan_chat.send_message(message)
            if success:
                print(f"📤 Message sent: {message}")
            else:
                print("❌ Failed to send message (no peers or encryption not ready)")
        except Exception as e:
            print(f"❌ Failed to send message: {e}")

    def send_image_to_peers(self, path: str):  # ← added
        """Manually send an image file (PNG) to peers."""
        try:
            if self.lan_chat.get_connection_count() == 0:
                print("ℹ️  No peers connected.")
                return
            ok = self.lan_chat.send_image(path)
            print("📤 Image sent to peers" if ok else "❌ Failed to send image")
        except Exception as e:
            print(f"❌ Error sending image: {e}")

    def hide_message(self, image_path, message):
        try:
            path = self.steganography.hide_message(image_path, message)
            if path:
                print(f"✅ Message hidden in: {path}")
            else:
                print("❌ Failed to hide message")
        except Exception as e:
            print(f"❌ Error hiding message: {e}")

    def reveal_message(self, image_path):
        try:
            msg = self.steganography.reveal_message(image_path)
            if msg:
                print(f"🔍 Revealed message: {msg}")
            else:
                print("❌ No message found or failed to reveal")
        except Exception as e:
            print(f"❌ Error revealing message: {e}")

    def generate_qr_code(self, ip, port_s):
        try:
            port = int(port_s)
            out = self.qr_pairing.generate_connect_qr(ip, port, "connect_qr.png")
            print(f"✅ QR code generated: {out} (contains ip+port; auto-connect on scan)")
        except Exception as e:
            print(f"❌ Error generating QR: {e}")

    def scan_qr_code(self):
        print("📷 Starting camera for QR scanning...")
        try:
            payload = self.qr_pairing.scan_qr_code(timeout=30)
            if not payload:
                print("❌ No QR decoded or scan cancelled")
                return
            ip = payload.get("ip")
            port = payload.get("port")
            if ip and port:
                print(f"🔗 Pairing found — connecting to {ip}:{port} ...")
                ok = self.lan_chat.connect_to_peer(ip, int(port))
                print("✅ Connected" if ok else "❌ Connect failed")
            else:
                print(f"ℹ️  Scanned data (no ip/port): {payload}")
        except Exception as e:
            print(f"❌ QR scan error: {e}")

    def shutdown(self):
        print("\n🛑 Shutting down Quantum-Secure Chat...")
        self.is_running = False
        try:
            self.lan_chat.stop()
        except Exception:
            pass
        print("👋 Application closed successfully!")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Quantum-Secure Chat Application")
    parser.add_argument("--port", type=int, default=23456, help="Port to use (default: 23456)")
    parser.add_argument("--no-crypto", action="store_true", help="Disable quantum cryptography")
    return parser.parse_args()


def main():
    args = parse_arguments()
    app = QuantumSecureChat(port=args.port, enable_crypto=not args.no_crypto)
    try:
        app.start()
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user")
    except Exception:
        print("❌ Fatal error occurred while running application:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
