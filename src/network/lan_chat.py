import socket
import threading
import json
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.logger import setup_logger


class LANChat:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.socket = None
        self.connections = []
        self.running = False
        self.logger = setup_logger("LANChat")

    def start_server(self):
        """Start the chat server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True

            self.logger.info(f"🚀 Server started on {self.host}:{self.port}")
            self.logger.info("Waiting for connections...")

            while self.running:
                try:
                    conn, addr = self.socket.accept()
                    self.connections.append(conn)
                    self.logger.info(f"✅ New connection from {addr}")

                    # Start a thread to handle this client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error accepting connection: {e}")

        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")

    def handle_client(self, conn, addr):
        """Handle messages from a client"""
        try:
            while self.running:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break

                self.logger.info(f"📨 Received from {addr}: {data}")

                # Broadcast to all other clients
                self.broadcast(data, conn)

        except Exception as e:
            self.logger.error(f"Error handling client {addr}: {e}")
        finally:
            conn.close()
            if conn in self.connections:
                self.connections.remove(conn)
            self.logger.info(f"❌ Connection closed: {addr}")

    def broadcast(self, message, sender_conn):
        """Send message to all connected clients except sender"""
        disconnected = []
        for conn in self.connections:
            if conn != sender_conn:
                try:
                    conn.send(message.encode('utf-8'))
                except:
                    disconnected.append(conn)

        # Remove disconnected clients
        for conn in disconnected:
            self.connections.remove(conn)

    def connect_to_peer(self, peer_ip, peer_port):
        """Connect to another chat instance"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, peer_port))
            self.connections.append(sock)

            # Start thread to listen for messages from this peer
            peer_thread = threading.Thread(
                target=self.handle_peer_messages,
                args=(sock, f"{peer_ip}:{peer_port}")
            )
            peer_thread.daemon = True
            peer_thread.start()

            self.logger.info(f"✅ Connected to peer: {peer_ip}:{peer_port}")
            return sock

        except Exception as e:
            self.logger.error(f"Failed to connect to {peer_ip}:{peer_port}: {e}")
            return None

    def handle_peer_messages(self, sock, peer_address):
        """Handle incoming messages from a peer"""
        try:
            while self.running:
                data = sock.recv(1024).decode('utf-8')
                if not data:
                    break
                self.logger.info(f"📨 Message from {peer_address}: {data}")
        except:
            self.logger.info(f"❌ Peer disconnected: {peer_address}")

    def send_message(self, message, target_sock=None):
        """Send a message to a specific connection or broadcast"""
        if target_sock:
            try:
                target_sock.send(message.encode('utf-8'))
            except:
                self.logger.error("Failed to send message")
        else:
            self.broadcast(message, None)

    def stop(self):
        """Stop the server and clean up"""
        self.running = False
        if self.socket:
            self.socket.close()
        for conn in self.connections:
            conn.close()
        self.connections.clear()
        self.logger.info("🛑 Server stopped")


# Simple test function
def test_lan_chat():
    """Test the LAN chat functionality"""
    chat = LANChat()

    # Start server in background thread
    server_thread = threading.Thread(target=chat.start_server)
    server_thread.daemon = True
    server_thread.start()

    return chat


if __name__ == "__main__":
    print("Testing LAN Chat...")
    chat = test_lan_chat()
    input("Press Enter to stop...")
    chat.stop()