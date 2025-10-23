import socket
import threading
import json
import time
from src.utils.logger import setup_logger


class LANChat:
    def __init__(self, host='0.0.0.0', port=23456):
        self.host = host
        self.port = port
        self.socket = None
        self.connections = []
        self.connection_info = {}
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

            while self.running:
                try:
                    conn, addr = self.socket.accept()
                    self.connections.append(conn)
                    self.connection_info[conn] = {
                        'address': addr,
                        'connected_at': time.time()
                    }

                    self.logger.info(f"✅ New connection from {addr}")

                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()

                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error accepting connection: {e}")

        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise

    def handle_client(self, conn, addr):
        """Handle messages from a client"""
        try:
            while self.running:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break

                try:
                    message_data = json.loads(data)
                    if 'type' in message_data and message_data['type'] == 'chat':
                        message = message_data['content']
                    else:
                        message = data
                except:
                    message = data

                self.logger.info(f"📨 Received from {addr}: {message}")
                self.broadcast(message, conn)

        except Exception as e:
            self.logger.error(f"Error handling client {addr}: {e}")
        finally:
            self.close_connection(conn, addr)

    def broadcast(self, message, sender_conn):
        """Send message to all connected clients except sender"""
        disconnected = []
        for conn in self.connections:
            if conn != sender_conn:
                try:
                    message_data = json.dumps({
                        'type': 'chat',
                        'content': message,
                        'timestamp': time.time()
                    })
                    conn.send(message_data.encode('utf-8'))
                except:
                    disconnected.append(conn)

        for conn in disconnected:
            self.close_connection(conn, "disconnected during broadcast")

    def connect_to_peer(self, peer_ip, peer_port):
        """Connect to another chat instance"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer_ip, peer_port))
            self.connections.append(sock)

            self.connection_info[sock] = {
                'address': (peer_ip, peer_port),
                'connected_at': time.time()
            }

            peer_thread = threading.Thread(
                target=self.handle_peer_messages,
                args=(sock, f"{peer_ip}:{peer_port}"),
                daemon=True
            )
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

                try:
                    message_data = json.loads(data)
                    message = message_data.get('content', data)
                except:
                    message = data

                self.logger.info(f"📨 Message from {peer_address}: {message}")
        except:
            self.logger.info(f"❌ Peer disconnected: {peer_address}")
        finally:
            self.close_connection(sock, peer_address)

    def send_message(self, message, target_sock=None):
        """Send a message to a specific connection or broadcast"""
        message_data = json.dumps({
            'type': 'chat',
            'content': message,
            'timestamp': time.time()
        })

        if target_sock:
            try:
                target_sock.send(message_data.encode('utf-8'))
                return True
            except:
                self.logger.error("Failed to send message to specific peer")
                return False
        else:
            self.broadcast(message, None)
            return True

    def get_connection_count(self):
        """Get number of active connections"""
        return len(self.connections)

    def get_connection_list(self):
        """Get list of active connections"""
        return [str(info['address']) for info in self.connection_info.values()]

    def close_connection(self, conn, identifier):
        """Close a connection and clean up"""
        try:
            conn.close()
        except:
            pass

        if conn in self.connections:
            self.connections.remove(conn)

        if conn in self.connection_info:
            del self.connection_info[conn]

        self.logger.info(f"❌ Connection closed: {identifier}")

    def stop(self):
        """Stop the server and clean up"""
        self.running = False
        if self.socket:
            self.socket.close()

        for conn in self.connections[:]:
            self.close_connection(conn, "shutdown")

        self.connections.clear()
        self.connection_info.clear()
        self.logger.info("🛑 Server stopped")


if __name__ == "__main__":
    print("Testing LAN Chat...")
    chat = LANChat()
    server_thread = threading.Thread(target=chat.start_server, daemon=True)
    server_thread.start()
    input("Press Enter to stop...")
    chat.stop()