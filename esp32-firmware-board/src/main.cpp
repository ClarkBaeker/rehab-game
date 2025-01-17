#include <WiFi.h>
#include <WebSocketsServer.h>
//#include <ESPmDNS.h>
#include "wifi_credentials.h"
#include <ArduinoJson.h>

WebSocketsServer webSocket = WebSocketsServer(81);

// This onWebSocketEvent() function only sends back a string to the client
/* void onWebSocketEvent(uint8_t client_num, WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char *)payload);
    if (message == "start_game") {
      // Trigger game logic on ESP32
      Serial.println("Game started!");
      webSocket.sendTXT(client_num, "ack_start_game");
    }
  }
} */

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
        // Implement your LED logic here
        /* if (led_id == 1) {
            digitalWrite(LED_BUILTIN, HIGH); // Example for built-in LED
        } */
    }
}

void onWebSocketEvent(uint8_t client_num, WStype_t type, uint8_t *payload, size_t length) {
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

  // Can be used to dynmaically discover the ESP using a hostname. Slower than IP address!!
  /* if (!MDNS.begin("esp32")) { // Hostname "esp32.local"
      Serial.println("Error starting mDNS");
  } else {
      Serial.println("mDNS responder started");
  } */

  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP()); // Print IP address
  
  webSocket.begin();
  webSocket.onEvent(onWebSocketEvent);
}

void loop() {
  webSocket.loop();
}
