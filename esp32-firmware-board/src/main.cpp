#include <WiFi.h>
#include <WebSocketsClient.h>
#include "wifi_credentials.h"

// WebSocket server address
const char* WS_SERVER_IP = "192.168.1.100"; // Replace with your computers's local IP
const int WS_SERVER_PORT = 8765;

// WebSocket client instance
WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char *)payload);
    // Trigger game logic on ESP32
    if (message == "start_game") {
      Serial.println("Message sent to client: " + message);
    }
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Connect to WebSocket server
  webSocket.begin(WS_SERVER_IP, WS_SERVER_PORT, "/");
  String message = "BoardESP";
  webSocket.sendTXT(message.c_str());
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void loop() {
  // Maintain WebSocket connection
    webSocket.loop();

  // Send a message every 5 seconds
  static unsigned long lastMessageTime = 0;
  if (millis() - lastMessageTime > 5000) {
      lastMessageTime = millis();
      String message = "Hello from ESP32!";
      webSocket.sendTXT(message.c_str());
      Serial.println("Message sent to server: " + message);
  }
}
