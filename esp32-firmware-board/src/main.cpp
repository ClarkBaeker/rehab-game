#include <WiFi.h>
#include <WebSocketsServer.h>
//#include <ESPmDNS.h>
#include "wifi_credentials.h"

WebSocketsServer webSocket = WebSocketsServer(81);

void onWebSocketEvent(uint8_t client_num, WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String message = String((char *)payload);
    if (message == "start_game") {
      // Trigger game logic on ESP32
      Serial.println("Game started!");
      webSocket.sendTXT(client_num, "ack_start_game");
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
