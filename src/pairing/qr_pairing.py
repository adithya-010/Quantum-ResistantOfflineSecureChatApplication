import json
import base64
import os
import tempfile
from src.utils.logger import setup_logger


class QRPairing:
    def __init__(self):
        self.logger = setup_logger("QRPairing")

    def generate_qr_code(self, data, output_path=None, size=10, border=5):
        """Generate QR code from data"""
        try:
            if isinstance(data, dict):
                data_str = json.dumps(data)
            else:
                data_str = str(data)

            # Use qrcode library if available
            try:
                import qrcode
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=size,
                    border=border,
                )

                qr.add_data(data_str)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                if output_path:
                    img.save(output_path)
                    self.logger.info(f"✅ QR code saved to: {output_path}")
                    return output_path
                else:
                    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    img.save(temp_file.name)
                    self.logger.info(f"✅ QR code saved to temporary file: {temp_file.name}")
                    return temp_file.name

            except ImportError:
                # Fallback: Create a text file with the data
                if output_path is None:
                    output_path = "qr_data.txt"

                with open(output_path, 'w') as f:
                    f.write(f"QR Data: {data_str}")

                self.logger.info(f"✅ QR data saved to: {output_path} (qrcode library not available)")
                return output_path

        except Exception as e:
            self.logger.error(f"Failed to generate QR code: {e}")
            return None

    def generate_pairing_qr(self, public_key, endpoint_info, output_path=None):
        """Generate pairing QR code with public key and connection info"""
        try:
            pairing_data = {
                'type': 'pairing',
                'public_key': base64.b64encode(public_key).decode('utf-8') if isinstance(public_key,
                                                                                         bytes) else public_key,
                'endpoint': endpoint_info,
                'version': '1.0'
            }

            return self.generate_qr_code(pairing_data, output_path)

        except Exception as e:
            self.logger.error(f"Failed to generate pairing QR: {e}")
            return None

    def scan_qr_code(self, camera_index=0, timeout=30):
        """Scan QR code from camera feed"""
        try:
            # Try to use OpenCV for QR scanning
            import cv2

            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                self.logger.error("❌ Cannot open camera")
                return None

            detector = cv2.QRCodeDetector()

            self.logger.info("📷 Camera started - Point camera at QR code...")
            print("Point camera at QR code. Press 'q' to quit.")

            start_time = cv2.getTickCount()
            timeout_ticks = timeout * cv2.getTickFrequency()

            while True:
                if (cv2.getTickCount() - start_time) > timeout_ticks:
                    self.logger.warning("⏰ QR scan timeout")
                    break

                ret, frame = cap.read()
                if not ret:
                    self.logger.error("❌ Failed to capture frame")
                    break

                data, bbox, _ = detector.detectAndDecode(frame)

                if bbox is not None:
                    bbox = bbox.astype(int)
                    for i in range(len(bbox)):
                        cv2.line(frame, tuple(bbox[i][0]), tuple(bbox[(i + 1) % len(bbox)][0]),
                                 color=(0, 255, 0), thickness=2)

                cv2.imshow("QR Code Scanner - Press 'q' to quit", frame)

                if data:
                    cap.release()
                    cv2.destroyAllWindows()

                    try:
                        parsed_data = json.loads(data)
                        self.logger.info("✅ QR code scanned and parsed successfully")
                        return parsed_data
                    except:
                        self.logger.info("✅ QR code scanned successfully")
                        return data

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            return None

        except ImportError:
            self.logger.error("❌ OpenCV not available for QR scanning")
            return "QR scanning requires OpenCV library"
        except Exception as e:
            self.logger.error(f"QR scanning failed: {e}")
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()
            return None

    def scan_qr_from_image(self, image_path):
        """Scan QR code from image file"""
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"Image file not found: {image_path}")
                return None

            import cv2
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return None

            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(image)

            if data:
                try:
                    parsed_data = json.loads(data)
                    self.logger.info(f"✅ QR code scanned from image: {image_path}")
                    return parsed_data
                except:
                    self.logger.info(f"✅ QR code scanned from image: {image_path}")
                    return data
            else:
                self.logger.warning(f"⚠️ No QR code found in image: {image_path}")
                return None

        except ImportError:
            self.logger.error("❌ OpenCV not available for QR scanning")
            return "OpenCV required for QR scanning"
        except Exception as e:
            self.logger.error(f"Failed to scan QR from image: {e}")
            return None


def test_qr_pairing():
    """Test QR pairing functionality"""
    qr = QRPairing()

    print("📱 Testing QR Pairing...")

    # Test data for pairing
    test_public_key = b"test_public_key_12345"
    test_endpoint = {"ip": "192.168.1.100", "port": 23456}

    # Generate pairing QR
    qr_path = qr.generate_pairing_qr(test_public_key, test_endpoint, "test_qr.png")
    if not qr_path:
        print("❌ Failed to generate QR code")
        return False

    if os.path.exists(qr_path):
        print("✅ QR code generation working")

        # Cleanup
        if os.path.exists("test_qr.png"):
            os.remove("test_qr.png")
    else:
        print("❌ QR code file not created")
        return False

    print("🎉 QR pairing tests completed!")
    return True


if __name__ == "__main__":
    test_qr_pairing()