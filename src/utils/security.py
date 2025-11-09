import hashlib
import hmac
import secrets
import os
import json
import base64
from datetime import datetime, timedelta
from src.utils.logger import setup_logger


class SecurityManager:
    """Manages security operations including key validation and secure tokens"""

    def __init__(self):
        self.logger = setup_logger("SecurityManager")
        self.session_keys = {}  # Store session keys for active connections

    def generate_session_id(self):
        """Generate a cryptographically secure session ID"""
        return secrets.token_urlsafe(32)

    def generate_salt(self, length=32):
        """Generate a random salt for key derivation"""
        return secrets.token_bytes(length)

    def hash_password(self, password, salt=None):
        """Hash a password with optional salt using PBKDF2"""
        if salt is None:
            salt = self.generate_salt()

        # Use PBKDF2 with SHA-256
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000  # iterations
        )

        return {
            'hash': base64.b64encode(key).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }

    def verify_password(self, password, password_hash, salt):
        """Verify a password against a hash"""
        try:
            salt_bytes = base64.b64decode(salt)
            result = self.hash_password(password, salt_bytes)
            return hmac.compare_digest(result['hash'], password_hash)
        except Exception as e:
            self.logger.error(f"Password verification failed: {e}")
            return False

    def generate_mac(self, message, key):
        """Generate HMAC for message authentication"""
        if isinstance(message, str):
            message = message.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')

        mac = hmac.new(key, message, hashlib.sha256)
        return base64.b64encode(mac.digest()).decode('utf-8')

    def verify_mac(self, message, mac_value, key):
        """Verify HMAC for message authentication"""
        try:
            expected_mac = self.generate_mac(message, key)
            return hmac.compare_digest(expected_mac, mac_value)
        except Exception as e:
            self.logger.error(f"MAC verification failed: {e}")
            return False

    def validate_ip_address(self, ip):
        """Validate IP address format"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except:
            return False

    def validate_port(self, port):
        """Validate port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except:
            return False

    def is_local_ip(self, ip):
        """Check if IP is in local network range"""
        local_ranges = [
            ('10.0.0.0', '10.255.255.255'),
            ('172.16.0.0', '172.31.255.255'),
            ('192.168.0.0', '192.168.255.255'),
            ('127.0.0.0', '127.255.255.255')
        ]

        try:
            ip_parts = [int(x) for x in ip.split('.')]
            ip_num = (ip_parts[0] << 24) + (ip_parts[1] << 16) + (ip_parts[2] << 8) + ip_parts[3]

            for start, end in local_ranges:
                start_parts = [int(x) for x in start.split('.')]
                end_parts = [int(x) for x in end.split('.')]

                start_num = (start_parts[0] << 24) + (start_parts[1] << 16) + (start_parts[2] << 8) + start_parts[3]
                end_num = (end_parts[0] << 24) + (end_parts[1] << 16) + (end_parts[2] << 8) + end_parts[3]

                if start_num <= ip_num <= end_num:
                    return True

            return False
        except:
            return False

    def sanitize_input(self, user_input, max_length=1000):
        """Sanitize user input to prevent injection attacks"""
        if not isinstance(user_input, str):
            return str(user_input)[:max_length]

        # Remove potentially dangerous characters
        sanitized = user_input.strip()[:max_length]

        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')

        return sanitized

    def create_session_token(self, peer_id, expiry_minutes=60):
        """Create a session token for a peer"""
        session_id = self.generate_session_id()
        expiry = datetime.now() + timedelta(minutes=expiry_minutes)

        token_data = {
            'session_id': session_id,
            'peer_id': peer_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': expiry.isoformat()
        }

        self.session_keys[session_id] = token_data
        return session_id

    def validate_session_token(self, session_id):
        """Validate a session token"""
        if session_id not in self.session_keys:
            return False

        token_data = self.session_keys[session_id]
        expiry = datetime.fromisoformat(token_data['expires_at'])

        if datetime.now() > expiry:
            del self.session_keys[session_id]
            return False

        return True

    def revoke_session(self, session_id):
        """Revoke a session token"""
        if session_id in self.session_keys:
            del self.session_keys[session_id]
            self.logger.info(f"Session revoked: {session_id}")
            return True
        return False

    def secure_random_bytes(self, length):
        """Generate cryptographically secure random bytes"""
        return secrets.token_bytes(length)

    def constant_time_compare(self, a, b):
        """Constant-time comparison to prevent timing attacks"""
        return hmac.compare_digest(a, b)