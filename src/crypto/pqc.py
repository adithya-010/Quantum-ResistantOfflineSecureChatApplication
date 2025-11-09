"""
pqc.py - Post-Quantum Cryptography abstraction layer.

This module supports:
- OQS (Kyber512) for key exchange and AES-GCM symmetric encryption
- Fallback to X25519 (built-in) when OQS is unavailable
"""

import os
import secrets

# Check if liboqs is installed
try:
    import oqs
    _HAS_OQS = True
except ImportError:
    _HAS_OQS = False

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class QuantumCrypto:
    def __init__(self):
        self.backend = "oqs" if _HAS_OQS else "fallback"
        self.server_keypair = None
        self.shared_secret = None
        self.aesgcm = None

    # 1️⃣ --- Server side KEM key pair ---
    def server_generate_kem_keypair(self):
        """
        Generate server (listening side) KEM key pair.
        Returns public key in bytes and stores the key object.
        """
        if self.backend == "oqs":
            kem = oqs.Kem("Kyber512")
            public_key = kem.generate_keypair()
            self.server_keypair = kem
            return public_key  # bytes
        else:  # fallback: X25519
            priv = x25519.X25519PrivateKey.generate()
            pub = priv.public_key()
            self.server_keypair = priv
            return pub.public_bytes()

    def server_public_bytes(self, public_key):
        """Return public key bytes (always bytes for Kyber)."""
        return public_key

    # 2️⃣ --- Client encapsulation ---
    def client_encapsulate(self, server_public_key: bytes):
        """
        Client side: encapsulate using server's public key.
        Returns ciphertext and shared_secret.
        """
        if self.backend == "oqs":
            kem = oqs.Kem("Kyber512")
            ciphertext, shared_secret = kem.encap_secret(server_public_key)
            return ciphertext, shared_secret
        else:
            server_pub = x25519.X25519PublicKey.from_public_bytes(server_public_key)
            client_priv = x25519.X25519PrivateKey.generate()
            shared = client_priv.exchange(server_pub)
            self.server_keypair = client_priv  # re-use holder for fallback
            return client_priv.public_key().public_bytes(), shared

    # 3️⃣ --- Server decapsulation ---
    def server_decapsulate(self, ciphertext: bytes):
        """
        Server side: decapsulate ciphertext to derive shared secret.
        """
        if self.backend == "oqs":
            kem = self.server_keypair
            shared_secret = kem.decap_secret(ciphertext)
            return shared_secret
        else:
            server_priv = self.server_keypair
            peer_pub = x25519.X25519PublicKey.from_public_bytes(ciphertext)
            shared = server_priv.exchange(peer_pub)
            return shared

    # 4️⃣ --- AESGCM binding ---
    def derive_aesgcm(self, shared_secret: bytes):
        """Derive AESGCM cipher using 256-bit key."""
        key = shared_secret[:32]
        self.aesgcm = AESGCM(key)

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt with AESGCM (nonce||ciphertext)."""
        if not self.aesgcm:
            raise RuntimeError("AESGCM not initialized")
        nonce = secrets.token_bytes(12)
        ct = self.aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ct

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt AESGCM (nonce||ciphertext)."""
        if not self.aesgcm:
            raise RuntimeError("AESGCM not initialized")
        nonce, ct = ciphertext[:12], ciphertext[12:]
        return self.aesgcm.decrypt(nonce, ct, None)

