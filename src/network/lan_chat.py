import socket
import threading
from utils.logger import get_logger

logger = get_logger("LANChat")

class LANChat:
    def __init__(self, host="0.0.0.0", port=12346, username="User"):
        self.host = host
        self.port = port
        self.username = username
        self.server_socket = None
        self.peers = {}  # (ip,port):socket
        self.running = True

    # --- SERVER HANDLER ---
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logger.info(f"Listening for peers on {self.host}:{self.port} ...")

        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                self.peers[addr] = conn
                logger.info(f"✅ Connected: {addr}")
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except Exception as e:
                logger.error(f"Server error: {e}")
                break

    # --- CLIENT CONNECT ---
    def connect_to_peer(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            self.peers[(ip, port)] = s
            threading.Thread(target=self.handle_client, args=(s, (ip, port)), daemon=True).start()
            logger.info(f"🤝 Connected to peer {ip}:{port}")
        except Exception as e:
            logger.error(f"Connection failed: {e}")

    # --- MESSAGE BROADCAST ---
    def broadcast_message(self, message):
        full_msg = f"[{self.username}] {message}"
        for addr, sock in list(self.peers.items()):
            try:
                sock.sendall(full_msg.encode())
            except Exception:
                logger.warning(f"Lost connection to {addr}")
                del self.peers[addr]
        logger.info(f"📤 Sent: {message}")

    # --- RECEIVE HANDLER ---
    def handle_client(self, conn, addr):
        while self.running:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                logger.info(f"💬 {data.decode()}")
            except Exception:
                break
        conn.close()
        if addr in self.peers:
            del self.peers[addr]
        logger.warning(f"❌ Disconnected: {addr}")

    # --- STATUS/UTILS ---
    def list_peers(self):
        if not self.peers:
            logger.info("No active peers.")
        for addr in self.peers:
            logger.info(f"Peer: {addr}")

    def show_status(self):
        logger.info(f"Listening on {self.host}:{self.port} | Peers: {len(self.peers)}")

    def close_all(self):
        self.running = False
        for s in self.peers.values():
            try:
                s.close()
            except Exception:
                pass
        if self.server_socket:
            self.server_socket.close()
        logger.info("All connections closed.")
