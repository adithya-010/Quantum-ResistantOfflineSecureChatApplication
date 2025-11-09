import cv2
import json
import qrcode
import time


class QRPairing:
    def generate_connect_qr(self, ip, port, out_path="connect_qr.png"):
        data = {"ip": ip, "port": port}
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(json.dumps(data))
        qr.make()
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(out_path)
        return out_path

    def scan_qr_code(self, timeout=30, show_camera=True):
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        start = time.time()

        print("🔍 Point your camera at a QR code...")

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            if show_camera:
                cv2.imshow("QR Scanner - Press q to cancel", frame)

            data, bbox, _ = detector.detectAndDecode(frame)
            if data:
                print("✅ QR code detected!")
                try:
                    payload = json.loads(data)
                except Exception:
                    payload = {"raw": data}
                cap.release()
                cv2.destroyAllWindows()
                return payload

            if (time.time() - start) > timeout:
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("🛑 Scan cancelled by user.")
                break

        cap.release()
        cv2.destroyAllWindows()
        return None
