#include <WiFi.h>
#include <WebSocketsClient.h>
#include "wifi_credentials.h"
#include <ArduinoJson.h>
#include <Wire.h>
#include <ICM20948_WE.h>
#include "Adafruit_DRV2605.h"

ICM20948_WE imu1 = ICM20948_WE(0x69);
ICM20948_WE imu2 = ICM20948_WE(0x68);

Adafruit_DRV2605 drv;  // vibromotor

long int t0 = millis();
uint8_t drive = 0;
bool is_motor_on = false;
double angle = 0;

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
    if (strcmp(command, "turn_on") == 0) {
        Serial.printf("Turning on motors");
        is_motor_on = true;
    }
    if (strcmp(command, "turn_off") == 0) {
        Serial.printf("Turning off motors");
        is_motor_on = false;
    }
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_CONNECTED) {
        // Send unique identifier when connected to server
        Serial.println("WebSocket connected!");
        webSocket.sendTXT("KneeESP");
        isWebSocketConnected = true;
  }
  if (type == WStype_DISCONNECTED) {
        Serial.println("WebSocket disconnected!");
        isWebSocketConnected = false;
  }
  if (type == WStype_TEXT) {
    handleWebSocketMessage(payload, length);
  }
}

void sendAngle(void *parameter) {
  while (true) {
    if(is_motor_on) {
      if (isWebSocketConnected) {
        String message;
        JsonDocument doc;
        doc["field"] = "angle";
        doc["value"] = angle;

        serializeJson(doc, message);
        webSocket.sendTXT(message.c_str());
        Serial.println("Message sent to server: " + message);
      } else {
          Serial.println("Angle could not be sent. WebSocket not connected");
      }
    }
    vTaskDelay(pdMS_TO_TICKS(300));
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

  Wire.begin();
  imu1.init();
  imu2.init();
  Serial.println("IMUs initialized");

  imu1.setAccRange(ICM20948_ACC_RANGE_2G);
  imu2.setAccRange(ICM20948_ACC_RANGE_2G);
  
  /*  Choose a level for the Digital Low Pass Filter or switch it off.  
   *  ICM20948_DLPF_0, ICM20948_DLPF_2, ...... ICM20948_DLPF_7, ICM20948_DLPF_OFF 
   *  
   *  DLPF       3dB Bandwidth [Hz]      Output Rate [Hz]
   *    0              246.0               1125/(1+ASRD) (default)
   *    1              246.0               1125/(1+ASRD)
   *    2              111.4               1125/(1+ASRD)
   *    3               50.4               1125/(1+ASRD)
   *    4               23.9               1125/(1+ASRD)
   *    5               11.5               1125/(1+ASRD)
   *    6                5.7               1125/(1+ASRD) 
   *    7              473.0               1125/(1+ASRD)
   *    OFF           1209.0               4500
   *    
   *    ASRD = Accelerometer Sample Rate Divider (0...4095)
   *    You achieve lowest noise using level 6  
   */
  imu1.setAccDLPF(ICM20948_DLPF_6);
  imu2.setAccDLPF(ICM20948_DLPF_6);    
  
  /*  Acceleration sample rate divider divides the output rate of the accelerometer.
   *  Sample rate = Basic sample rate / (1 + divider) 
   *  It can only be applied if the corresponding DLPF is not off!
   *  Divider is a number 0...4095 (different range compared to gyroscope)
   *  If sample rates are set for the accelerometer and the gyroscope, the gyroscope
   *  sample rate has priority.
   */
  imu1.setAccSampleRateDivider(6); // fs = 179 Hz
  imu2.setAccSampleRateDivider(6); // = 1125 * loop_duration - 1

  drv.begin();
  // drv.setMode(DRV2605_MODE_REALTIME); // continuous drive
  Serial.println("Motors initialized");

  drv.selectLibrary(1);
  drv.setMode(DRV2605_MODE_INTTRIG); 

  Serial.print("\n");

  // Connect to WebSocket server
  webSocket.begin(WS_SERVER_IP, WS_SERVER_PORT, "/");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
  // Create a FreeRTOS task for sending the knee angle to the server
  xTaskCreatePinnedToCore(
      sendAngle,      // Task function
      "RepeatedTask", // Name
      10000,          // Stack size
      NULL,           // Parameters
      1,              // Priority
      NULL,           // Task handle
      1               // Core ID (0 or 1)
  );
}

void loop() {
  // Maintain WebSocket connection
  webSocket.loop();

  long int t = millis();
  imu1.readSensor();
  xyzFloat gvals1;
  imu1.getGValues( &gvals1 );
  xyzFloat gyr1;
  imu1.getGyrValues( &gyr1 );

  /*Serial.print(gvals1.x, 5); Serial.print(",");
  Serial.print(gvals1.y, 5); Serial.print(",");
  Serial.print(gvals1.z, 5); Serial.print(",");*/

  double norm1 = sqrt(gvals1.x*gvals1.x + gvals1.y*gvals1.y);
  double angle1 = acos(gvals1.x / norm1);

  imu2.readSensor();
  xyzFloat gvals2;
  imu2.getGValues(&gvals2);
  xyzFloat gyr2;
  imu2.getGyrValues(&gyr2);

  /*Serial.print(gvals2.x, 5); Serial.print(",");
  Serial.print(gvals2.y, 5); Serial.print(",");
  Serial.print(gvals2.z, 5); Serial.print(" ");*/

  double norm2 = sqrt(gvals2.x*gvals2.x + gvals2.y*gvals2.y);
  double angle2 = acos(gvals2.x / norm2);

  angle = (angle1 + angle2) * 57.29578; // in degrees
  // Serial.print(angle); Serial.print("\n");

  if (is_motor_on) {
    if (angle > 5) {
      if (angle > 15) drv.setWaveform(0, 14); // short pulses
      else drv.setWaveform(0, 47); // medium

    drv.setWaveform(1, 0); // end waveform
    drv.go();
    }
  }
  // Serial.print(millis() - t); Serial.print(",");
}
