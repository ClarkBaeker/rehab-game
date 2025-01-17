#include <WiFi.h>
#include <WebSocketsServer.h>
#include "wifi_credentials.h"
#include <ArduinoJson.h>

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {

}