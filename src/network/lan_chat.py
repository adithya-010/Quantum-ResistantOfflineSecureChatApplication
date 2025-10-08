# src/network/lan_chat.py
import socket
import threading
from src.utils.logger import get_logger
from liboqs import KeyEncapsulation, Sign
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

class LanChat:
    def __init__(self, username, logger, port=12346):
        self.username = username
        self.logger = logger
        self.port = port
        self.peers = {}  # (ip, port) : socket
        self.shared_keys = {}  # (ip, port) : symmetric key
        self.sign_keys = {}    # (ip, port) : sign key for verification
        self.running = True

        # Kyber Key Pair for key exchange
        self.kem = KeyEncapsulation('Kyber512')
        self.private_key, self.public_key = self.kem.generate_keypair()

        # Dilithium keys for signing
        self.sign = Sign('Dilithium2')
        self.sign_private, self.sign_public = self.sign.generate_keypair()

        # Start server thread
        self.server_thread = threading.Thread(target=self._start_server, daemon=True)
        self.server_thread.start()
        self.logger.info(f"Server started on port {self.port}")

    def _start_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('0.0.0.0', self.port))
        server_sock.listen(5)

        while self.running:
            try:
                client_sock, addr = server_sock.accept()
                self.logger.info(f"Incoming connection from {addr}")
                threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True).start()
            except Exception as e:
                self.logger.error(f"Server error: {e}")

    def _handle_client(self, client_sock, addr):
        self.peers[addr] = client_sock
        # Key exchange on first connect
        try:
            # Send our public key and signature
            client_sock.send(self.public_key)
            client_sock.send(self.sign_public)
        except Exception as e:
            self.logger.error(f"Failed to send keys to {addr}: {e}")

        while self.running:
            try:
                data = client_sock.recv(4096)
                if not data:
                    break
                # For now just print encrypted data
                print(f"\n🔒 [Encrypted Message from {addr}] {data.hex()[:60]}...")
            except Exception as e:
                self.logger.error(f"Client error {addr}: {e}")
                break
        client_sock.close()
        del self.peers[addr]
        self.logger.info(f"Connection closed: {addr}")

    def connect(self, ip, port):
        try:
            peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_sock.connect((ip, port))
            self.peers[(ip, port)] = peer_sock
            threading.Thread(target=self._handle_client, args=(peer_sock, (ip, port)), daemon=True).start()
            self.logger.info(f"Connected to peer {ip}:{port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to {ip}:{port} - {e}")

    def send_message(self, message):
        for addr, peer_sock in self.peers.items():
            try:
                # For now sending plain text; we will later encrypt with shared key
                peer_sock.send(message.encode())
            except Exception as e:
                self.logger.error(f"Failed to send message to {addr} - {e}")

    def list_peers(self):
        if not self.peers:
            print("No connected peers.")
        else:
            for addr in self.peers:
                print(f"- {addr}")

    def show_status(self):
        print(f"Connected peers: {len(self.peers)}")

    def shutdown(self):
        self.running = False
        for peer_sock in self.peers.values():
            try:
                peer_sock.close()
            except:
                pass
        self.peers.clear()
        self.logger.info("LAN Chat shutdown complete.")
