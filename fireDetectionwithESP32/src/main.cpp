#include <WiFi.h>
#include <Arduino.h>
#include <PubSubClient.h>

const char *wifiSSID = "Galaxy A05s 3010";
const char *wifiPassword = "09090909";

const char *mqtt_server = "192.168.145.91";
const char *mqtt_topic = "api/deteksi";

const int led = 12;

void koneksiMqtt();
void koneksiWifi();
void callback(char *topic, byte *payload, unsigned int length);

WiFiClient espClient;
PubSubClient client(espClient);

void setup()
{
  Serial.begin(115200);

  pinMode(led, OUTPUT);

  koneksiWifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback); // Menyambungkan callback untuk menerima pesan MQTT
  koneksiMqtt();
}

void loop()
{
  if (!client.connected())
  {
    koneksiMqtt();
  }
  client.loop();
  delay(500);
}

void koneksiWifi()
{
  Serial.println("Menghubungkan ke jaringan WiFi...");
  WiFi.begin(wifiSSID, wifiPassword);
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nWiFi terhubung!");
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void koneksiMqtt()
{
  Serial.println("Menghubungkan ke MQTT...");
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client"))
    {
      Serial.println("Terhubung ke broker MQTT");
      client.subscribe(mqtt_topic);
    }
    else
    {
      Serial.print("Gagal, rc = ");
      Serial.println(client.state());
      delay(2000);
    }
  }
}

void callback(char *topic, byte *payload, unsigned int length)
{
  String message = "";
  for (int i = 0; i < length; i++)
  {
    message += (char)payload[i];
  }
  message.trim();
  Serial.print("Pesan diterima: ");
  Serial.println(message);

  if (message == "API TERDETEKSI")
  {
    digitalWrite(led, HIGH);
    Serial.println("LED Menyala");
  }
  else if (message == "TIDAK ADA API")
  {
    digitalWrite(led, LOW);
    Serial.println("LED Mati");
  }
  else
  {
    Serial.println("Pesan tidak dikenali");
  }
}
