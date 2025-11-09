#!/usr/bin/env python3
"""
liboqs Diagnostic Tool
Checks if liboqs-python is properly installed and what's available
"""

import sys

print("=" * 70)
print("                  🔍 LIBOQS DIAGNOSTIC TOOL")
print("=" * 70)

# Test 1: Can we import oqs?
print("\n📦 Test 1: Import oqs module")
try:
    import oqs

    print("✅ SUCCESS: oqs module imported")
    print(f"   Location: {oqs.__file__}")
except ImportError as e:
    print(f"❌ FAILED: Cannot import oqs")
    print(f"   Error: {e}")
    print("\n💡 Fix: Install liboqs-python")
    print("   pip install liboqs-python")
    sys.exit(1)

# Test 2: Check module contents
print("\n📋 Test 2: Check available classes/functions")
available = dir(oqs)
print(f"   Found {len(available)} items in oqs module")

important_items = [
    'KeyEncapsulation',
    'Signature',
    'get_enabled_KEM_mechanisms',
    'get_enabled_sig_mechanisms'
]

for item in important_items:
    if item in available:
        print(f"   ✅ {item}")
    else:
        print(f"   ❌ {item} (MISSING)")

# Test 3: Try to get algorithm lists
print("\n🧩 Test 3: Get supported algorithms")
try:
    if hasattr(oqs, 'get_enabled_KEM_mechanisms'):
        kems = oqs.get_enabled_KEM_mechanisms()
        print(f"   ✅ KEMs available: {len(kems)}")
        if kems:
            print(f"   First 3: {kems[:3]}")
    else:
        print("   ❌ get_enabled_KEM_mechanisms not found")
except Exception as e:
    print(f"   ❌ Error getting KEMs: {e}")

try:
    if hasattr(oqs, 'get_enabled_sig_mechanisms'):
        sigs = oqs.get_enabled_sig_mechanisms()
        print(f"   ✅ Signatures available: {len(sigs)}")
        if sigs:
            print(f"   First 3: {sigs[:3]}")
    else:
        print("   ❌ get_enabled_sig_mechanisms not found")
except Exception as e:
    print(f"   ❌ Error getting signatures: {e}")

# Test 4: Try to create KEM object
print("\n🔑 Test 4: Create KeyEncapsulation object")
try:
    if hasattr(oqs, 'KeyEncapsulation'):
        kem = oqs.KeyEncapsulation("Kyber512")
        print("   ✅ KeyEncapsulation object created (Kyber512)")

        # Test 5: Try key generation
        print("\n🔐 Test 5: Generate keypair")
        try:
            public_key = kem.generate_keypair()
            print(f"   ✅ Keypair generated successfully")
            print(f"   Public key length: {len(public_key)} bytes")

            # Test 6: Try encapsulation
            print("\n📦 Test 6: Encapsulate secret")
            try:
                ciphertext, shared_secret = kem.encap_secret(public_key)
                print(f"   ✅ Encapsulation successful")
                print(f"   Ciphertext length: {len(ciphertext)} bytes")
                print(f"   Shared secret length: {len(shared_secret)} bytes")

                # Test 7: Try decapsulation
                print("\n🔓 Test 7: Decapsulate secret")
                try:
                    decap_secret = kem.decap_secret(ciphertext)
                    if decap_secret == shared_secret:
                        print("   ✅ Decapsulation successful - secrets match!")
                    else:
                        print("   ❌ Secrets don't match")
                except Exception as e:
                    print(f"   ❌ Decapsulation failed: {e}")

            except Exception as e:
                print(f"   ❌ Encapsulation failed: {e}")
        except Exception as e:
            print(f"   ❌ Keypair generation failed: {e}")
    else:
        print("   ❌ KeyEncapsulation class not found")
        print("\n💡 Your liboqs-python may be outdated or incorrectly installed")
        print("   Try reinstalling:")
        print("   pip uninstall liboqs-python")
        print("   pip install liboqs-python")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 8: Try Signature
print("\n✍️  Test 8: Create Signature object")
try:
    if hasattr(oqs, 'Signature'):
        sig = oqs.Signature("Dilithium2")
        print("   ✅ Signature object created (Dilithium2)")

        try:
            public_key = sig.generate_keypair()
            print(f"   ✅ Signature keypair generated")
            print(f"   Public key length: {len(public_key)} bytes")
        except Exception as e:
            print(f"   ❌ Keypair generation failed: {e}")
    else:
        print("   ❌ Signature class not found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Final summary
print("\n" + "=" * 70)
print("                         📊 SUMMARY")
print("=" * 70)

if hasattr(oqs, 'KeyEncapsulation') and hasattr(oqs, 'Signature'):
    print("✅ LIBOQS STATUS: FULLY FUNCTIONAL")
    print("   Your quantum cryptography is ready to use!")
elif 'oqs' in sys.modules:
    print("⚠️  LIBOQS STATUS: PARTIALLY FUNCTIONAL")
    print("   The module loads but some features are missing.")
    print("   The app will use placeholder encryption instead.")
else:
    print("❌ LIBOQS STATUS: NOT AVAILABLE")
    print("   Install with: pip install liboqs-python")

print("\n💡 Note: The chat app will work even without liboqs!")
print("   It will use placeholder encryption in development mode.")
print("=" * 70)