# install_dependencies.py
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

dependencies = [
    "colorlog",
    "numpy",
    "opencv-python",
    "Pillow",
    "qrcode[pil]",
    "stegano",
    "cryptography",
    "psutil",
    "liboqs-python",
]

print("[🚀] Installing dependencies...")

for package in dependencies:
    try:
        install(package)
        print(f"[✔] {package} installed successfully")
    except Exception as e:
        print(f"[✖] Failed to install {package}: {e}")

print("[✅] All dependencies installation attempted")
