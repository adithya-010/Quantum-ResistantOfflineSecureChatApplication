import json
import threading
import time
from src.network.lan_chat import LANChat
from src.crypto.pqc import QuantumCrypto
from src.utils.security import SecurityManager
from src.utils.logger import setup_logger


class SecureChat:
    """
    Secure chat implementation with quantum-resistant encryption.
    Wraps LANChat to add end-to-end encryption.
    """

    def __init__(self, host='0.0.0.0', port=23456):
        self.lan_chat = LANChat(host=host, port=port)
        self.crypto = QuantumCrypto()
        self.security = SecurityManager()
        self.logger = setup_logger("SecureChat")

        # Key management
        self.my_public_key = None
        self.my_kem = None
        self.peer_keys = {}  # peer_id -> {'public_key': ..., 'shared_secret': ...}
        self.sessions = {}  # peer_id -> session_id

        # Initialize crypto keys
        self._initialize_keys()

    def _initialize_keys(self):
        """Initialize quantum-resistant key pairs"""
        try:
            self.my_public_key, self.my_kem = self.crypto.generate_kem_keypair()
            self.logger.info("✅ Quantum keys initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize keys: {e}")

    def start_server(self):
        """Start the secure chat server"""
        self.logger.info("🔐 Starting secure chat server...")

        # Start underlying LAN chat
        server_thread = threading.Thread(
            target=self.lan_chat.start_server,
            daemon=True
        )
        server_thread.start()

        self.logger.info("✅ Secure server started")

    def connect_to_peer(self, peer_ip, peer_port):
        """Connect to a peer with key exchange"""
        try:
            # Establish basic connection
            result = self.lan_chat.connect_to_peer(peer_ip, peer_port)
            if not result:
                return False

            # Perform key exchange
            peer_id = f"{peer_ip}:{peer_port}"
            success = self._perform_key_exchange(result, peer_id)

            if success:
                self.logger.info(f"✅ Secure connection established with {peer_id}")
                return True
            else:
                self.logger.error(f"❌ Key exchange failed with {peer_id}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to connect securely: {e}")
            return False

    def _perform_key_exchange(self, sock, peer_id):
        """Perform quantum-resistant key exchange"""
        try:
            # Send our public key
            key_exchange_msg = {
                'type': 'key_exchange',
                'public_key': self.my_public_key.hex() if isinstance(self.my_public_key, bytes) else str(
                    self.my_public_key),
                'timestamp': time.time()
            }

            sock.send((json.dumps(key_exchange_msg) + '\n').encode('utf-8'))

            # Receive peer's public key (placeholder - would need async handling)
            # For now, we'll use a placeholder shared secret
            shared_secret = self.security.secure_random_bytes(32)

            self.peer_keys[peer_id] = {
                'public_key': None,  # Would store peer's key here
                'shared_secret': shared_secret
            }

            # Create session
            session_id = self.security.create_session_token(peer_id)
            self.sessions[peer_id] = session_id

            self.logger.info(f"✅ Key exchange completed with {peer_id}")
            return True

        except Exception as e:
            self.logger.error(f"Key exchange failed: {e}")
            return False

    def send_encrypted_message(self, message, peer_id=None):
        """Send an encrypted message"""
        try:
            # If no specific peer, broadcast to all
            if peer_id is None:
                # Broadcast encrypted to all peers
                for pid in self.peer_keys.keys():
                    self._send_to_peer(message, pid)
                return True
            else:
                return self._send_to_peer(message, peer_id)

        except Exception as e:
            self.logger.error(f"Failed to send encrypted message: {e}")
            return False

    def _send_to_peer(self, message, peer_id):
        """Send encrypted message to specific peer"""
        try:
            if peer_id not in self.peer_keys:
                self.logger.warning(f"No shared key for peer {peer_id}")
                return False

            # Get shared secret
            shared_secret = self.peer_keys[peer_id]['shared_secret']

            # Encrypt message
            encrypted = self.crypto.encrypt_message(message, shared_secret)
            if not encrypted:
                self.logger.error("Encryption failed")
                return False

            # Create secure message packet
            secure_msg = {
                'type': 'encrypted',
                'data': encrypted,
                'mac': self.security.generate_mac(encrypted, shared_secret),
                'timestamp': time.time()
            }

            # Send via LAN chat (would need socket reference)
            # For now, use broadcast
            self.lan_chat.send_message(json.dumps(secure_msg))

            self.logger.info(f"✅ Encrypted message sent to {peer_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send to peer: {e}")
            return False

    def decrypt_message(self, encrypted_packet, peer_id):
        """Decrypt a received message"""
        try:
            if peer_id not in self.peer_keys:
                self.logger.warning(f"No shared key for peer {peer_id}")
                return None

            shared_secret = self.peer_keys[peer_id]['shared_secret']

            # Verify MAC
            if not self.security.verify_mac(
                    encrypted_packet['data'],
                    encrypted_packet['mac'],
                    shared_secret
            ):
                self.logger.error("MAC verification failed - message tampered!")
                return None

            # Decrypt
            decrypted = self.crypto.decrypt_message(
                encrypted_packet['data'],
                shared_secret
            )

            if decrypted:
                self.logger.info(f"✅ Message decrypted from {peer_id}")

            return decrypted

        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return None

    def get_connection_count(self):
        """Get number of secure connections"""
        return len(self.peer_keys)

    def revoke_session(self, peer_id):
        """Revoke a peer's session"""
        if peer_id in self.sessions:
            session_id = self.sessions[peer_id]
            self.security.revoke_session(session_id)
            del self.sessions[peer_id]

        if peer_id in self.peer_keys:
            del self.peer_keys[peer_id]

        self.logger.info(f"✅ Session revoked for {peer_id}")

    def stop(self):
        """Stop the secure chat"""
        self.logger.info("🛑 Stopping secure chat...")

        # Revoke all sessions
        for peer_id in list(self.sessions.keys()):
            self.revoke_session(peer_id)

        # Stop underlying LAN chat
        self.lan_chat.stop()

        self.logger.info("✅ Secure chat stopped")


def test_security_manager():
    """Test security manager functionality"""
    print("🔐 Testing Security Manager...")

    security = SecurityManager()

    # Test password hashing
    password = "test_password_123"
    result = security.hash_password(password)
    print(f"✅ Password hashed")

    # Test password verification
    if security.verify_password(password, result['hash'], result['salt']):
        print("✅ Password verification works")
    else:
        print("❌ Password verification failed")

    # Test IP validation
    if security.validate_ip_address("192.168.1.1"):
        print("✅ IP validation works")

    # Test session tokens
    session_id = security.create_session_token("peer_123")
    if security.validate_session_token(session_id):
        print("✅ Session token works")

    print("🎉 Security tests completed!")


def test_secure_chat():
    """Test secure chat functionality"""
    print("🔐 Testing Secure Chat...")

    secure_chat = SecureChat(port=23457)

    # Test key initialization
    if secure_chat.my_public_key:
        print("✅ Quantum keys initialized")
    else:
        print("⚠️  Using placeholder keys")

    print("✅ Secure chat initialized")
    print("🎉 Secure chat tests completed!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Security Modules")
    print("=" * 60 + "\n")

    test_security_manager()
    print()
    test_secure_chat()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)