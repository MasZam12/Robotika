import cv2
import numpy as np
import paho.mqtt.client as mqtt

def detect_fire(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_fire = np.array([0, 50, 200])
    upper_fire = np.array([25, 255, 255])
    mask = cv2.inRange(hsv, lower_fire, upper_fire)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return mask, contours

broker = "192.168.145.91"
port = 1883
topic = "api/deteksi"

def on_connect(client, userdata, flags, rc):
    print("Terhubung ke Broker MQTT dengan kode hasil: " + str(rc))

def on_message(client, userdata, msg):
    print(f"Pesan diterima di topik {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 60)

client.loop_start()

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Gagal membaca frame dari kamera")
            break

        mask, contours = detect_fire(frame)
        fire_detected = False

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                fire_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "API TERDETEKSI", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                print("API TERDETEKSI di area dengan luas:", area)

        # Kirim pesan MQTT berdasarkan deteksi
        if fire_detected:
            client.publish(topic, "API TERDETEKSI")
        else:
            client.publish(topic, "TIDAK ADA API")

        cv2.imshow("Deteksi Api", frame)
        cv2.imshow("Masker Api", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:
    print(f"Terjadi kesalahan: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    client.loop_stop()
    client.disconnect()
