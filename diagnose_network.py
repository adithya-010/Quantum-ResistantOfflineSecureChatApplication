#!/usr/bin/env python3
"""
Quantum-Secure Chat - Network Diagnostic Tool
"""

import socket
import subprocess
import platform
import os
import sys
import threading
import time


def print_banner():
    print("\n" + "=" * 60)
    print("           🔧 NETWORK DIAGNOSTIC TOOL")
    print("=" * 60)


def check_python_environment():
    print("\n🐍 CHECKING PYTHON ENVIRONMENT...")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.release()}")

    try:
        import socket
        print("✅ socket module: OK")
    except ImportError as e:
        print(f"❌ socket module: {e}")
        return False

    try:
        import threading
        print("✅ threading module: OK")
    except ImportError as e:
        print(f"❌ threading module: {e}")
        return False

    return True


def get_network_info():
    print("\n🌐 CHECKING NETWORK CONFIGURATION...")

    system = platform.system().lower()

    try:
        if system == "windows":
            result = subprocess.run(["ipconfig"], capture_output=True, text=True)
            print("Windows Network Info:")
            for line in result.stdout.split('\n'):
                if "IPv4" in line or "Address" in line:
                    print(f"  {line.strip()}")

        elif system == "darwin":
            result = subprocess.run(["ifconfig"], capture_output=True, text=True)
            print("macOS Network Info:")
            for line in result.stdout.split('\n'):
                if "inet " in line and "127.0.0.1" not in line:
                    print(f"  {line.strip()}")

        elif system == "linux":
            result = subprocess.run(["ip", "addr"], capture_output=True, text=True)
            print("Linux Network Info:")
            for line in result.stdout.split('\n'):
                if "inet " in line and "127.0.0.1" not in line:
                    print(f"  {line.strip()}")

    except Exception as e:
        print(f"❌ Failed to get network info: {e}")


def test_port_availability(port=23456):
    print(f"\n🔌 TESTING PORT {port} AVAILABILITY...")

    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('0.0.0.0', port))
        test_socket.listen(1)
        print(f"✅ Port {port} is available")
        test_socket.close()
        return True
    except OSError as e:
        print(f"❌ Port {port} is NOT available: {e}")
        return False


def test_basic_socket_communication():
    print("\n🔄 TESTING BASIC SOCKET COMMUNICATION...")

    def simple_server(port=34567):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('127.0.0.1', port))
            server_socket.listen(1)
            conn, addr = server_socket.accept()
            data = conn.recv(1024).decode()
            conn.send(f"ECHO: {data}".encode())
            conn.close()
            server_socket.close()
            return True
        except Exception as e:
            print(f"  Server error: {e}")
            return False

    def simple_client(port=34567):
        try:
            time.sleep(0.5)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', port))
            client_socket.send("TEST".encode())
            response = client_socket.recv(1024).decode()
            client_socket.close()
            return response == "ECHO: TEST"
        except Exception as e:
            print(f"  Client error: {e}")
            return False

    server_thread = threading.Thread(target=simple_server, daemon=True)
    server_thread.start()

    if simple_client():
        print("✅ Basic socket communication: WORKING")
        return True
    else:
        print("❌ Basic socket communication: FAILED")
        return False


def main():
    print_banner()

    tests = [
        ("Python Environment", check_python_environment),
        ("Network Configuration", get_network_info),
        ("Port Availability", lambda: test_port_availability(23456)),
        ("Basic Socket Communication", test_basic_socket_communication),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    print("\n" + "=" * 60)
    print("                   📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your environment should work.")
    else:
        print("🔧 Some tests failed. Follow recommendations below.")

    print("\n💡 TROUBLESHOOTING RECOMMENDATIONS:")
    print("1. 🔄 RESTART BOTH LAPTOPS")
    print("2. 🔥 DISABLE FIREWALL TEMPORARILY")
    print("3. 📡 CONNECT BOTH TO SAME WIFI")
    print("4. 🔌 USE DIFFERENT PORT: python main.py --port 34567")
    print("5. 🖥️ TEST LOCALHOST FIRST")
    print("=" * 60)


if __name__ == "__main__":
    main()