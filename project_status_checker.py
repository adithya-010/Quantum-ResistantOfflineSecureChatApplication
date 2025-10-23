#!/usr/bin/env python3
"""
Quantum-Secure Chat - Project Status Checker
"""

import os
import sys
import subprocess
import importlib
import platform
import json
from pathlib import Path


class ProjectStatusChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = {
            "project_structure": {},
            "dependencies": {},
            "functionality": {}
        }

    def print_banner(self):
        print("\n" + "=" * 70)
        print("           🔒 QUANTUM-SECURE CHAT - PROJECT STATUS CHECKER")
        print("=" * 70)
        print(f"📋 Python: {sys.version.split()[0]}")
        print(f"💻 Platform: {platform.system()} {platform.release()}")
        print("=" * 70)

    def check_project_structure(self):
        print("\n📁 CHECKING PROJECT STRUCTURE...")

        required_structure = {
            "directories": [
                "src",
                "src/network",
                "src/crypto",
                "src/pairing",
                "src/steganography",
                "src/utils"
            ],
            "files": [
                "main.py",
                "simple_test.py",
                "diagnose_network.py",
                "project_status_checker.py",
                "requirements.txt",
                "src/network/__init__.py",
                "src/network/lan_chat.py",
                "src/crypto/__init__.py",
                "src/crypto/pqc.py",
                "src/pairing/__init__.py",
                "src/pairing/qr_pairing.py",
                "src/steganography/__init__.py",
                "src/steganography/stego.py",
                "src/utils/__init__.py",
                "src/utils/logger.py"
            ]
        }

        self.results["project_structure"] = {"passed": 0, "failed": 0, "details": []}

        for directory in required_structure["directories"]:
            dir_path = self.project_root / directory
            if dir_path.exists():
                self.results["project_structure"]["passed"] += 1
                self.results["project_structure"]["details"].append(f"✅ Directory: {directory}")
            else:
                self.results["project_structure"]["failed"] += 1
                self.results["project_structure"]["details"].append(f"❌ Missing directory: {directory}")

        for file in required_structure["files"]:
            file_path = self.project_root / file
            if file_path.exists():
                self.results["project_structure"]["passed"] += 1
                self.results["project_structure"]["details"].append(f"✅ File: {file}")
            else:
                self.results["project_structure"]["failed"] += 1
                self.results["project_structure"]["details"].append(f"❌ Missing file: {file}")

        for detail in self.results["project_structure"]["details"]:
            print(detail)

        return self.results["project_structure"]["failed"] == 0

    def check_dependencies(self):
        print("\n📦 CHECKING DEPENDENCIES...")

        dependencies = {
            "Essential": [
                {"import": "qrcode", "pip": "qrcode[pil]", "essential": True},
                {"import": "PIL", "pip": "Pillow", "essential": True},
                {"import": "cv2", "pip": "opencv-python", "essential": True},
                {"import": "stegano", "pip": "stegano", "essential": True},
            ],
            "Quantum Crypto": [
                {"import": "liboqs", "pip": "liboqs-python", "essential": False},
            ],
            "Optional": [
                {"import": "cryptography", "pip": "cryptography", "essential": False},
                {"import": "websockets", "pip": "websockets", "essential": False},
            ]
        }

        self.results["dependencies"] = {"passed": 0, "failed": 0, "missing": []}

        for category, packages in dependencies.items():
            print(f"\n🔍 {category}:")
            for package in packages:
                try:
                    if package["import"] == "PIL":
                        importlib.import_module("PIL.Image")
                    else:
                        importlib.import_module(package["import"])

                    status = "✅" if package["essential"] else "✓"
                    print(f"  {status} {package['import']}")
                    self.results["dependencies"]["passed"] += 1
                except ImportError:
                    status = "❌" if package["essential"] else "⚠️"
                    print(f"  {status} {package['import']} - pip install {package['pip']}")
                    self.results["dependencies"]["failed"] += 1
                    self.results["dependencies"]["missing"].append(package)

        return self.results["dependencies"]["failed"] == 0

    def check_functionality(self):
        print("\n🧪 CHECKING FUNCTIONALITY...")

        sys.path.insert(0, str(self.project_root))

        functionality_tests = [
            {
                "name": "Logger Module",
                "test": "from src.utils.logger import setup_logger; logger = setup_logger('Test'); logger.info('Logger working')",
            },
            {
                "name": "LAN Chat Module",
                "test": "from src.network.lan_chat import LANChat; chat = LANChat(); print('LANChat initialized')",
            },
            {
                "name": "Steganography",
                "test": "from stegano import lsb; print('Steganography available')",
            },
            {
                "name": "QR Code Generation",
                "test": "import qrcode; qr = qrcode.QRCode(version=1, box_size=10, border=5); print('QR generation working')",
            }
        ]

        self.results["functionality"] = {"passed": 0, "failed": 0, "details": []}

        for test in functionality_tests:
            try:
                exec(test["test"])
                self.results["functionality"]["passed"] += 1
                self.results["functionality"]["details"].append(f"✅ {test['name']}")
                print(f"✅ {test['name']}")
            except Exception as e:
                self.results["functionality"]["failed"] += 1
                self.results["functionality"]["details"].append(f"❌ {test['name']}: {e}")
                print(f"❌ {test['name']}: {e}")

        return self.results["functionality"]["failed"] == 0

    def install_missing_dependencies(self):
        if not self.results["dependencies"]["missing"]:
            return True

        print(f"\n🚀 INSTALLING {len(self.results['dependencies']['missing'])} MISSING DEPENDENCIES...")

        success_count = 0
        for package in self.results["dependencies"]["missing"]:
            print(f"\n📦 Installing {package['pip']}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package["pip"]])
                print(f"✅ Successfully installed {package['pip']}")
                success_count += 1
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package['pip']}")

        return success_count == len(self.results["dependencies"]["missing"])

    def generate_report(self):
        print("\n" + "=" * 70)
        print("                       📊 COMPREHENSIVE STATUS REPORT")
        print("=" * 70)

        print(
            f"\n📁 PROJECT STRUCTURE: {self.results['project_structure']['passed']} passed, {self.results['project_structure']['failed']} failed")
        print(
            f"📦 DEPENDENCIES: {self.results['dependencies']['passed']} passed, {self.results['dependencies']['failed']} failed")
        print(
            f"🧪 FUNCTIONALITY: {self.results['functionality']['passed']} passed, {self.results['functionality']['failed']} failed")

        print("\n💡 RECOMMENDATIONS:")
        if self.results["project_structure"]["failed"] > 0:
            print("   • Create missing files and directories")

        if self.results["dependencies"]["failed"] > 0:
            print("   • Install missing dependencies")

        print("\n🚀 NEXT STEPS:")
        if all([self.results["project_structure"]["failed"] == 0,
                self.results["dependencies"]["failed"] == 0,
                self.results["functionality"]["failed"] == 0]):
            print("   🎉 ALL SYSTEMS GO! Run: python main.py")
        else:
            print("   🔧 Fix the issues above, then run this checker again")

        print("=" * 70)

    def run_complete_check(self):
        self.print_banner()

        structure_ok = self.check_project_structure()
        deps_ok = self.check_dependencies()
        func_ok = self.check_functionality()

        if not deps_ok:
            install = input("\n🤖 Install missing dependencies? (y/n): ").lower().strip()
            if install == 'y':
                self.install_missing_dependencies()
                self.check_dependencies()

        self.generate_report()

        return all([structure_ok, deps_ok, func_ok])


def main():
    checker = ProjectStatusChecker()
    success = checker.run_complete_check()

    with open("project_status.json", "w") as f:
        json.dump(checker.results, f, indent=2)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()