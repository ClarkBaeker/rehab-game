#include <WiFi.h>
#include <WebSocketsClient.h>
#include "wifi_credentials.h"
#include <ArduinoJson.h>

const int LED = 17; // GPIO pin for LED

// WebSocket server address (ip address needs to be specified in wifi_credentials.h)
const int WS_SERVER_PORT = 8765;

// WebSocket client instance
WebSocketsClient webSocket;
bool isWebSocketConnected = false; // Track connection status

void handleWebSocketMessage(uint8_t *payload, size_t length) {
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error) {
        Serial.print("JSON Parsing failed: ");
        Serial.println(error.c_str());
        return;
    }
    const char* command = doc["command"];
    int led_id = doc["led_id"];
    if (strcmp(command, "turn_on") == 0) {
        Serial.printf("Turning on LED %d\n", led_id);
        digitalWrite(LED, HIGH);
        // Implement your LED logic here
        /* if (led_id == 1) {
            digitalWrite(LED_BUILTIN, HIGH); // Example for built-in LED
        } */
    }
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_CONNECTED) {
        // Send unique identifier
        Serial.println("WebSocket connected!");
        webSocket.sendTXT("BoardESP");
        isWebSocketConnected = true;
  }
  if (type == WStype_TEXT) {
    handleWebSocketMessage(payload, length);
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

  pinMode(LED, OUTPUT);

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
