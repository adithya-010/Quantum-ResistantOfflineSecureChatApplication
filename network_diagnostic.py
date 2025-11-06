#!/usr/bin/env python3
"""
Network Diagnostic Tool for Quantum Chat
Helps troubleshoot connection issues
"""

import socket
import subprocess
import platform
import sys


def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Unable to determine"


def check_port_open(host, port, timeout=5):
    """Check if a port is open on a host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.gaierror:
        return False
    except Exception as e:
        print(f"Error checking port: {e}")
        return False


def ping_host(host):
    """Ping a host to check if it's reachable"""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]

    try:
        output = subprocess.run(command, capture_output=True, timeout=5)
        return output.returncode == 0
    except:
        return False


def scan_local_network(port=23456):
    """Scan local network for chat servers"""
    local_ip = get_local_ip()
    if local_ip == "Unable to determine":
        print("❌ Cannot determine local IP")
        return []

    # Get network prefix (e.g., 192.168.1)
    network_prefix = '.'.join(local_ip.split('.')[:-1])

    print(f"🔍 Scanning {network_prefix}.* for servers on port {port}...")
    print("   This may take a minute...\n")

    found_servers = []
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        if check_port_open(ip, port, timeout=0.5):
            found_servers.append(ip)
            print(f"✅ Found server at {ip}:{port}")

    return found_servers


def main():
    print("=" * 60)
    print("     🔍 QUANTUM CHAT NETWORK DIAGNOSTICS")
    print("=" * 60)

    # Get local info
    hostname = socket.gethostname()
    local_ip = get_local_ip()

    print(f"\n📍 Your Information:")
    print(f"   Hostname: {hostname}")
    print(f"   Local IP: {local_ip}")
    print(f"   OS: {platform.system()} {platform.release()}")

    # Check if server is running locally
    print(f"\n🔌 Checking local server (port 23456)...")
    if check_port_open('localhost', 23456):
        print("   ✅ Server is running locally")
    else:
        print("   ❌ Server is NOT running locally")
        print("   💡 Start the server first: python main.py")

    # Get target IP
    print("\n" + "=" * 60)
    target_ip = input("Enter target IP to test (or press Enter to scan network): ").strip()

    if target_ip:
        print(f"\n🎯 Testing connection to {target_ip}...")

        # Ping test
        print(f"   📡 Pinging {target_ip}...")
        if ping_host(target_ip):
            print(f"   ✅ Host is reachable")
        else:
            print(f"   ❌ Host is NOT reachable")
            print(f"   💡 Check if the device is on the same network")

        # Port test
        print(f"   🔌 Checking port 23456...")
        if check_port_open(target_ip, 23456):
            print(f"   ✅ Port 23456 is OPEN")
            print(f"   💡 Connection should work! Try: connect {target_ip} 23456")
        else:
            print(f"   ❌ Port 23456 is CLOSED or FILTERED")
            print(f"   💡 Possible issues:")
            print(f"      - Server not running on {target_ip}")
            print(f"      - Firewall blocking port 23456")
            print(f"      - Wrong IP address")
    else:
        # Scan network
        found = scan_local_network()
        if found:
            print(f"\n✅ Found {len(found)} server(s)")
            print("\n💡 Try connecting with:")
            for ip in found:
                print(f"   connect {ip} 23456")
        else:
            print("\n❌ No servers found on the local network")
            print("\n💡 Troubleshooting steps:")
            print("   1. Ensure the server is running on the target device")
            print("   2. Check firewall settings")
            print("   3. Verify both devices are on the same network")

    print("\n" + "=" * 60)
    print("Diagnostic complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Diagnostic cancelled")
        sys.exit(0)