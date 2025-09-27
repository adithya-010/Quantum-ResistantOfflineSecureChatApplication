#!/usr/bin/env python3
"""
Library Checker for Quantum-Secure Chat Application
Checks if all required packages are installed and working
"""

import sys
import subprocess
import importlib

# Required packages with their import names and pip names
REQUIRED_PACKAGES = [
    # Core packages
    {"import": "socket", "pip": None, "builtin": True},  # Built-in Python
    {"import": "threading", "pip": None, "builtin": True},  # Built-in Python
    {"import": "json", "pip": None, "builtin": True},  # Built-in Python
    {"import": "logging", "pip": None, "builtin": True},  # Built-in Python

    # External packages
    {"import": "qrcode", "pip": "qrcode[pil]"},
    {"import": "PIL", "pip": "Pillow"},  # Pillow is imported as PIL
    {"import": "numpy", "pip": "numpy"},
    {"import": "cv2", "pip": "opencv-python"},
    {"import": "websockets", "pip": "websockets"},
    {"import": "cryptography", "pip": "cryptography"},
    {"import": "stegano", "pip": "stegano"},
]

# Future packages (for later phases)
FUTURE_PACKAGES = [
    {"import": "liboqs", "pip": "liboqs-python"},
    {"import": "PyQt5", "pip": "pyqt5"},
]


def check_package(package_info):
    """Check if a package is installed and can be imported"""
    package_name = package_info["import"]
    is_builtin = package_info.get("builtin", False)

    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        if is_builtin:
            print(f"❌ {package_name} (BUILT-IN - This is very unusual!)")
        else:
            print(f"❌ {package_name}")
        return False


def install_package(package_info):
    """Install a package using pip"""
    if package_info.get("builtin") or package_info["pip"] is None:
        return True  # Skip built-in packages

    package_name = package_info["pip"]
    print(f"📦 Installing {package_name}...")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}")
        return False


def main():
    print("🔍 Checking required packages...")
    print("=" * 50)

    missing_packages = []

    # Check Phase 1 packages (LAN Chat)
    print("Phase 1 - LAN Chat Packages:")
    for package in REQUIRED_PACKAGES[:8]:  # First 8 packages (including built-ins)
        if not check_package(package):
            if not package.get("builtin"):
                missing_packages.append(package)

    print("\nPhase 2-3 - Future Packages:")
    for package in REQUIRED_PACKAGES[8:] + FUTURE_PACKAGES:  # Remaining packages
        check_package(package)

    # Install missing packages
    if missing_packages:
        print(f"\n🚀 Installing {len(missing_packages)} missing packages...")
        print("=" * 50)

        for package in missing_packages:
            install_package(package)

        # Verify installation
        print("\n🔍 Verifying installation...")
        print("=" * 50)
        all_installed = True
        for package in missing_packages:
            if not check_package(package):
                all_installed = False

        if all_installed:
            print("\n🎉 All packages installed successfully!")
        else:
            print("\n⚠️  Some packages may still need manual installation")
    else:
        print("\n🎉 All required packages are already installed!")

    # Test basic functionality
    print("\n🧪 Testing basic imports...")
    try:
        from src.utils.logger import setup_logger
        from src.network.lan_chat import LANChat
        print("✅ Project modules import correctly!")
    except ImportError as e:
        print(f"❌ Project module import issue: {e}")


if __name__ == "__main__":
    main()