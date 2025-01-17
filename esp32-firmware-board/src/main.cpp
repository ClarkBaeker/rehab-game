#include <WiFi.h>
#include <WebSocketsClient.h>
#include "wifi_credentials.h"
#include <ArduinoJson.h>

// WebSocket server address (ip address needs to be specified in wifi_credentials.h)
const int WS_SERVER_PORT = 8765;

// WebSocket client instance
WebSocketsClient webSocket;
bool isWebSocketConnected = false; // Track connection status

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_CONNECTED) {
        // Send unique identifier
        Serial.println("WebSocket connected!");
        webSocket.sendTXT("BoardESP");
        isWebSocketConnected = true;
  }
  if (type == WStype_TEXT) {
    String message = String((char *)payload);
    // Trigger game logic on ESP32
    if (message == "Turn on LED 1") {
      Serial.println("Message received from server: " + message);
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
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void loop() {
  // Maintain WebSocket connection
  webSocket.loop();

  // Send a message every 5 seconds
  static unsigned long lastMessageTime = 0;
  if (isWebSocketConnected && millis() - lastMessageTime > 5000) {
      lastMessageTime = millis();
      String message = "Hello from ESP32!";
      webSocket.sendTXT(message.c_str());
      Serial.println("Message sent to server: " + message);
  }
}
