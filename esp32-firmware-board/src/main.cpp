#include <WiFi.h>
#include <WebSocketsClient.h>
#include "wifi_credentials.h"
#include <ArduinoJson.h>
#include <map>


std::map<int, int> led_map = {
    {0, 19},
    {1, 25},
    {2, 26},
    {3, 4},
    {4, 5},
    {5, 18},
    {6, 27},
    {7, 12},
    {8, 13},
    {9, 32},
    {10, 15},
    {11, 33},
    // {12, x},
    // {13, x},
};


// WebSocket server address (ip address needs to be specified in wifi_credentials.h)
const int WS_SERVER_PORT = 8765;

// WebSocket client instance
WebSocketsClient webSocket;
bool isWebSocketConnected = false;

void handleWebSocketMessage(uint8_t *payload, size_t length) {
  // Parse JSON message
  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  if (error) {
      Serial.print("JSON Parsing failed: ");
      Serial.println(error.c_str());
      return;
  }
  
  // Deconstruct JSON message
  const char* command = doc["command"];
  int led_id = doc["led_id"];

  // Handle command
  if (strcmp(command, "turn_on") == 0) {
      Serial.printf("Turning on LED %d\n", led_id);
      digitalWrite(led_map[led_id], HIGH);
  }
  if (strcmp(command, "turn_off") == 0) {
      Serial.printf("Turning off LED %d\n", led_id);
      digitalWrite(led_map[led_id], LOW);
  }
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_CONNECTED) {
        // Send unique identifier when connected to server
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

  // Set up LED pins
  std::map<int, int>::iterator it;
  for (it = led_map.begin(); it != led_map.end(); it++) {
    Serial.print("Setting pin ");
    Serial.println(it->second);
    pinMode(it->second, OUTPUT);
  }

  // Turn off all LEDs
  for (it = led_map.begin(); it != led_map.end(); it++) {
    digitalWrite(it->second, LOW);
  }

  // Connect to WebSocket server
  webSocket.begin(WS_SERVER_IP, WS_SERVER_PORT, "/");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void loop() {
  // Maintain WebSocket connection
  webSocket.loop();
}
