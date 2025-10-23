#!/usr/bin/env python3
"""
Ultra-Simple Chat Test
Bare minimum functionality to isolate issues
"""

import socket
import threading
import time
import sys


class SimpleChat:
    def __init__(self, port=23456):
        self.port = port
        self.running = False
        self.connections = []

    def start_server(self):
        """Simple server that echoes messages"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"🚀 SIMPLE SERVER STARTED on port {self.port}")
            print("💡 Others can connect to you")
            print("📨 Messages will be echoed back")

            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    self.connections.append(conn)
                    print(f"✅ Connected to {addr}")

                    # Handle client in thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    client_thread.start()

                except Exception as e:
                    if self.running:
                        print(f"Error: {e}")

        except Exception as e:
            print(f"❌ Failed to start server: {e}")

    def handle_client(self, conn, addr):
        """Handle messages from client"""
        try:
            while self.running:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break

                print(f"📨 From {addr}: {data}")

                # Echo back
                conn.send(f"ECHO: {data}".encode('utf-8'))

        except Exception as e:
            print(f"Error with {addr}: {e}")
        finally:
            conn.close()
            if conn in self.connections:
                self.connections.remove(conn)
            print(f"❌ Disconnected: {addr}")

    def connect_to_peer(self, ip, port):
        """Connect to another chat instance"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            self.connections.append(sock)

            print(f"✅ Connected to {ip}:{port}")

            # Start listening for messages
            peer_thread = threading.Thread(
                target=self.listen_to_peer,
                args=(sock, f"{ip}:{port}"),
                daemon=True
            )
            peer_thread.start()

            return sock

        except Exception as e:
            print(f"❌ Failed to connect to {ip}:{port}: {e}")
            return None

    def listen_to_peer(self, sock, peer_name):
        """Listen for messages from peer"""
        try:
            while self.running:
                data = sock.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"📨 From {peer_name}: {data}")
        except:
            print(f"❌ Peer disconnected: {peer_name}")

    def send_message(self, message):
        """Send message to all connected peers"""
        disconnected = []
        for conn in self.connections:
            try:
                conn.send(message.encode('utf-8'))
            except:
                disconnected.append(conn)

        for conn in disconnected:
            self.connections.remove(conn)

    def stop(self):
        """Stop the server"""
        self.running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()
        for conn in self.connections:
            conn.close()
        self.connections.clear()
        print("🛑 Server stopped")


def main():
    print("=" * 50)
    print("           💬 ULTRA-SIMPLE CHAT TEST")
    print("=" * 50)
    print("This is the simplest possible chat to test networking")
    print("=" * 50)

    chat = SimpleChat(port=23456)

    try:
        # Start server in background
        server_thread = threading.Thread(target=chat.start_server, daemon=True)
        server_thread.start()

        time.sleep(1)  # Let server start

        print("\n💡 COMMANDS:")
        print("  connect <IP> <port>  - Connect to peer")
        print("  send <message>       - Send message")
        print("  quit                 - Exit")
        print("\nExample: connect 192.168.1.100 23456")
        print("Example: send Hello World!")
        print("-" * 50)

        while True:
            try:
                user_input = input("simple-chat> ").strip()

                if not user_input:
                    continue

                parts = user_input.split()
                command = parts[0].lower()

                if command == "connect" and len(parts) == 3:
                    chat.connect_to_peer(parts[1], int(parts[2]))

                elif command == "send" and len(parts) > 1:
                    message = " ".join(parts[1:])
                    chat.send_message(message)
                    print(f"📤 Sent: {message}")

                elif command == "quit":
                    break

                else:
                    print("❌ Unknown command")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    finally:
        chat.stop()


if __name__ == "__main__":
    main()