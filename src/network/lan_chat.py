import socket
import threading
import json
import base64
import os
import traceback

from src.crypto.pqc import QuantumCrypto


class LANChat:
    """
    TCP chat with newline-delimited JSON frames.
    Performs a Kyber-based or X25519 handshake, then encrypts all messages/files.
    """

    def __init__(self, port=23456):
        self.port = int(port)
        self.server_socket = None
        self.connections = []  # list of dict: {sock, addr, shared}
        self._stop_flag = threading.Event()
        self.qc = QuantumCrypto()

        # Directory to save received files
        self.recv_dir = os.path.join(os.getcwd(), "received")
        os.makedirs(self.recv_dir, exist_ok=True)

    # ---------------- Server ----------------
    def start_server(self):
        self._stop_flag.clear()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(8)
        while not self._stop_flag.is_set():
            try:
                self.server_socket.settimeout(1.0)
                client_sock, addr = self.server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True).start()

    def stop(self):
        self._stop_flag.set()
        try:
            if self.server_socket:
                self.server_socket.close()
        except Exception:
            pass
        for c in list(self.connections):
            try:
                c["sock"].close()
            except Exception:
                pass
        self.connections.clear()

    def _handle_client(self, sock, addr):
        conn = {"sock": sock, "addr": addr, "shared": None}
        self.connections.append(conn)
        try:
            # --- Server side handshake ---
            server_keyobj = self.qc.server_generate_kem_keypair()
            server_pub = self.qc.server_public_bytes(server_keyobj)
            self._send_json(sock, {"type": "handshake_server_pub", "public": base64.b64encode(server_pub).decode()})

            msg = self._recv_json(sock)
            if not msg or msg.get("type") != "handshake_client_blob":
                raise RuntimeError("Invalid handshake from client")
            blob = base64.b64decode(msg["blob"])
            shared = self.qc.server_finalize(server_keyobj, blob)
            conn["shared"] = shared

            # --- Receive loop (encrypted frames) ---
            while True:
                frm = self._recv_json(sock)
                if not frm:
                    break
                ftype = frm.get("type")
                if ftype == "message":
                    self._handle_encrypted_message(conn, frm)
                elif ftype == "file":
                    self._handle_encrypted_file(conn, frm)

        except Exception:
            traceback.print_exc()
        finally:
            try:
                sock.close()
            except Exception:
                pass
            if conn in self.connections:
                self.connections.remove(conn)

    # ---------------- Client (dialer) ----------------
    def connect_to_peer(self, ip, port) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((ip, int(port)))
        conn = {"sock": sock, "addr": (ip, int(port)), "shared": None}
        self.connections.append(conn)

        # --- Client handshake ---
        msg = self._recv_json(sock)
        if not msg or msg.get("type") != "handshake_server_pub":
            sock.close()
            self.connections.remove(conn)
            return False
        server_pub = base64.b64decode(msg["public"])
        blob, shared = self.qc.client_encapsulate(server_pub)
        self._send_json(sock, {"type": "handshake_client_blob", "blob": base64.b64encode(blob).decode()})
        conn["shared"] = shared

        # Reader thread
        threading.Thread(target=self._reader_for_conn, args=(conn,), daemon=True).start()
        return True

    def _reader_for_conn(self, conn):
        sock = conn["sock"]
        try:
            while True:
                frm = self._recv_json(sock)
                if not frm:
                    break
                ftype = frm.get("type")
                if ftype == "message":
                    self._handle_encrypted_message(conn, frm)
                elif ftype == "file":
                    self._handle_encrypted_file(conn, frm)
        except Exception:
            traceback.print_exc()
        finally:
            try:
                sock.close()
            except Exception:
                pass
            if conn in self.connections:
                self.connections.remove(conn)

    # ---------------- Public API ----------------
    def send_message(self, plaintext: str) -> bool:
        ok_any = False
        for conn in list(self.connections):
            try:
                shared = conn.get("shared")
                if not shared:
                    continue
                nonce, ct = self.qc.encrypt(shared, plaintext.encode())
                self._send_json(conn["sock"], {
                    "type": "message",
                    "nonce": base64.b64encode(nonce).decode(),
                    "ciphertext": base64.b64encode(ct).decode()
                })
                ok_any = True
            except Exception:
                traceback.print_exc()
        return ok_any

    def send_image(self, path: str) -> bool:
        """Send an image file (PNG only) to all connected peers."""
        if not os.path.isfile(path):
            print(f"❌ File not found: {path}")
            return False

        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception as e:
            print(f"❌ Read error: {e}")
            return False

        fname = os.path.basename(path)
        ok_any = False
        for conn in list(self.connections):
            try:
                shared = conn.get("shared")
                if not shared:
                    continue

                # Build inner payload JSON and encrypt it
                inner = json.dumps({
                    "filename": fname,
                    "b64": base64.b64encode(data).decode(),
                }).encode()

                nonce, ct = self.qc.encrypt(shared, inner)
                self._send_json(conn["sock"], {
                    "type": "file",
                    "nonce": base64.b64encode(nonce).decode(),
                    "ciphertext": base64.b64encode(ct).decode()
                })
                ok_any = True
            except Exception:
                traceback.print_exc()

        return ok_any

    def get_connection_count(self) -> int:
        return len(self.connections)

    # ---------------- Frame handlers ----------------
    def _handle_encrypted_message(self, conn, frm):
        try:
            nonce = base64.b64decode(frm["nonce"])
            ct = base64.b64decode(frm["ciphertext"])
            pt = self.qc.decrypt(conn["shared"], nonce, ct)
            self.on_plaintext_received(conn["addr"], pt.decode(errors="replace"))
        except Exception:
            print("❌ decrypt error (message)")

    def _handle_encrypted_file(self, conn, frm):
        """Decrypt and save incoming file payload."""
        try:
            nonce = base64.b64decode(frm["nonce"])
            ct = base64.b64decode(frm["ciphertext"])
            pt = self.qc.decrypt(conn["shared"], nonce, ct)
            payload = json.loads(pt.decode())
            fname = payload.get("filename", "file.bin")
            raw = base64.b64decode(payload.get("b64", ""))

            # Ensure unique filename
            base = os.path.splitext(fname)[0]
            ext = os.path.splitext(fname)[1] or ".png"
            out = os.path.join(self.recv_dir, fname)
            i = 1
            while os.path.exists(out):
                out = os.path.join(self.recv_dir, f"{base}_{i}{ext}")
                i += 1

            with open(out, "wb") as f:
                f.write(raw)

            print(f"📥 Image received: {out}")
        except Exception:
            print("❌ decrypt/save error (file)")
            traceback.print_exc()

    # ---------------- Helpers ----------------
    def _send_json(self, sock, obj):
        data = (json.dumps(obj) + "\n").encode()
        sock.sendall(data)

    def _recv_json(self, sock):
        buf = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                return None
            buf += chunk
            if b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                try:
                    return json.loads(line.decode())
                except Exception:
                    return None

    # Hook to integrate with your UI/logging
    def on_plaintext_received(self, addr, message: str):
        print(f"📥 From {addr}: {message}")
